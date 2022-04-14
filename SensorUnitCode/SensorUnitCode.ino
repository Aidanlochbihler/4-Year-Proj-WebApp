#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <SD.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
Adafruit_MPU6050 mpu;
/*

Pin Layout
GPS Module:
Green Line (GPS TX) -> Pin 3
White Line (GPS RX) -> Pin 4
5V power
Ground

SD Card Module:
CS Line -> Pin 10
DI Line -> Pin 11
DO Line -> Pin 12
CLK Line -> Pin 13
5V power
Ground

Notes:
- The GPS module from cold will take 8-15 seconds to "warm up", ie you will get INVALID as output for LAT LONG
  after 10s it should start to work
- When dealing with arudino components you need to be conscious of what your baud rate is set at
  there is the Serial Baud rate which you can set to many things but make sure your serial monitor is set to the same baud rate
  or you won't see anything.
  The GPS module also has its own Baud rate mine was 9600 but yours could be 4800 
*/

File myFile;
const int ledPin = 5;
const int onoffPin = 7;
static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;
int count = 0;
float min_accel_x = 0;
float min_accel_y = 0;
float min_accel_z = 0;
float max_accel_x = 0;
float max_accel_y = 0;
float max_accel_z = 0;

float x_var = 0;
float y_var = 0;
float z_var = 0;
float last_sec = -1;
long randNumber;
String filename;
int down_direction = 0; //0->X, 1->Y, 2->Z for the Accelerometer

// The TinyGPS++ object
TinyGPSPlus gps;


// The serial connection to the GPS device
SoftwareSerial ss(RXPin, TXPin);

void setup(void)
{
  //**HAVE THE SENSOR SYNC ITSELF ON START UP FOR ACCEL**
  
  Serial.begin(115200);
  //--------------------------------------------------------------------------------------------------------
  ss.begin(GPSBaud);

  pinMode(ledPin, OUTPUT); 
  pinMode(onoffPin, OUTPUT);

  digitalWrite(onoffPin, HIGH);
  digitalWrite(ledPin, HIGH);
  
  Serial.println(F("GPS CODE AIDAN LOCHBIHLER"));
  Serial.println();

  Serial.print("Initializing SD card...");
  pinMode(10, OUTPUT);
  if (!SD.begin(10)) {
    Serial.println("initialization failed!");
    
  }else{
    Serial.println("initialization done.");
  }

    randomSeed(analogRead(0));
    randNumber = random(1,1000000);
    String myString = String(randNumber);
    
    filename = "F"+myString+".txt"; //MUST FOLLOW: “NAME001” is an 8 character or fewer string, and “EXT” is a 3 character extension
    Serial.println(filename);
  
  while(SD.exists(filename)){
    Serial.println("File Exists Trying again.");
    randomSeed(analogRead(0));
    randNumber = random(1,1000000);
    String myString = String(randNumber);
    
    filename = "F"+myString+".txt";
    Serial.println(filename);
  }

//  filename = "test.txt";
  myFile = SD.open(filename, FILE_WRITE);


  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to test.txt...");
    myFile.println("GPS STARTED");
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.println("ERROR ERROR ERROR opening test.txt");
    digitalWrite(onoffPin, LOW); 
//    while(true); //stops code *************************************
  }

  Serial.println("Finding Accelerometer");
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");

  }else{
  Serial.println("MPU6050 Found!");
  }
  // set accelerometer range to +-8G
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);

  // set gyro range to +- 500 deg/s
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);

  // set filter bandwidth to 21 Hz
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  delay(10);

  sync_accel();
 
}
static inline int8_t sgn(int val) {
  if (val < 0) return 1;
  if (val==0) return 0;
  return -1;
}
void sync_accel(){
  float x_sum = 0;
  float y_sum = 0;
  float z_sum = 0;
  for (int i = 0; i < 10; ++i)
  {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    x_sum = x_sum + a.acceleration.x;
    y_sum = y_sum + a.acceleration.y;
    z_sum = z_sum + a.acceleration.z;
    Serial.print(" X: "); Serial.print(a.acceleration.x);
    Serial.print(" Y: "); Serial.print(a.acceleration.y);
    Serial.print(" Z: "); Serial.print(a.acceleration.z);
    Serial.println();
    
    delay(100);
    printf("%d ", i);
  }

  float x = x_sum/10;
  float y = y_sum/10;
  float z = z_sum/10;
  //******************************************************************************************
  //Compare the absolute value of (a-CONST), (b-CONST) and (c-CONST). Whichever absolute value is lowest, that one is closest.
  if (abs(abs(x) - 9.81) <= abs(abs(y) - 9.81) && abs(abs(x) - 9.81) <= abs(abs(z) - 9.81)){
    down_direction = 0;
    //x_var = 9.81*sgn(x);
    Serial.println("Down is X");
  }
  else if(abs(abs(y) - 9.81) <= abs(abs(x) - 9.81) && abs(abs(y) - 9.81) <= abs(abs(z) - 9.81)){
    down_direction = 1;
    //y_var = 9.81*sgn(y);
    Serial.println("Down is Y");
  }
  else if(abs(abs(z) - 9.81) <= abs(abs(y) - 9.81) && abs(abs(z) - 9.81) <= abs(abs(x) - 9.81)){
    down_direction = 2;
    //z_var = 9.81*sgn(z);
    Serial.println("Down is Z");
  }
  //******************************************************************************************
  
}

void loop()
{ 

  while (ss.available() > 0){
    if (gps.encode(ss.read())) 
      displayInfo();
  }
  if (millis() > 5000 && gps.charsProcessed() < 10){
    Serial.println(F("No GPS detected: check wiring."));
    while(true);
  }
}
//----------------------------------------------------

void print_latlong(){
    
    Serial.print(F(" Lat: ")); Serial.print(gps.location.lat(), 6); 
    Serial.print(F(" Long: ")); Serial.print(gps.location.lng(), 6);
    
    myFile.print(F(" Lat: ")); myFile.print(gps.location.lat(), 6);
    myFile.print(F(" Long: ")); myFile.print(gps.location.lng(), 6);
}

void print_date(){ //Split 
    //2022-01-04T18:24:03+00:00
    //YYYY-MM-DDThh:mm:ss 
    
    Serial.print(F("Date/Time: "));
    Serial.print(gps.date.year()); Serial.print(F("-"));
    if (gps.date.month()<10){
      Serial.print("0");
      Serial.print(gps.date.month()); Serial.print(F("-"));
    }else{
      Serial.print(gps.date.month()); Serial.print(F("-"));
    }

    if (gps.date.day()<10){
      Serial.print("0");
      Serial.print(gps.date.day()); Serial.print(F("T"));
    }else{
      Serial.print(gps.date.day()); Serial.print(F("T"));
    }
    
    
    
    myFile.print(F("Date/Time: "));
    myFile.print(gps.date.year()); myFile.print(F("-"));
    if (gps.date.month()<10){
      myFile.print("0");
      myFile.print(gps.date.month()); myFile.print(F("-"));
    }else{
      myFile.print(gps.date.month()); myFile.print(F("-"));}


    if (gps.date.day()<10){
      myFile.print("0");
      myFile.print(gps.date.day()); myFile.print(F("T"));
    }else{
      myFile.print(gps.date.day()); myFile.print(F("T"));
    }


}

void print_time(){ //Split 
    if (gps.time.hour() < 10) Serial.print(F("0"));
    Serial.print(gps.time.hour()); Serial.print(F(":"));
    if (gps.time.minute() < 10) Serial.print(F("0"));
    Serial.print(gps.time.minute()); Serial.print(F(":"));
    if (gps.time.second() < 10) Serial.print(F("0"));
    Serial.print(gps.time.second()); Serial.print(F("."));
    if (gps.time.centisecond() < 10) Serial.print(F("0"));
    Serial.print(gps.time.centisecond());

    if (gps.time.hour() < 10) myFile.print(F("0"));
    myFile.print(gps.time.hour()); myFile.print(F(":"));
    if (gps.time.minute() < 10) myFile.print(F("0"));
    myFile.print(gps.time.minute()); myFile.print(F(":"));
    if (gps.time.second() < 10) myFile.print(F("0"));
    myFile.print(gps.time.second()); myFile.print(F("."));
    if (gps.time.centisecond() < 10) myFile.print(F("0"));
    myFile.print(gps.time.centisecond()); 
}

//This fuction will ensure that the "Z:" in the string will always respresent the accel "towards earth" ie should always be 9.81 when still
void print_accel(){
      if (down_direction == 0){ // X is down
        Serial.print(" MINX: "); Serial.print(min_accel_z);
        Serial.print(" MINY: "); Serial.print(min_accel_y);
        Serial.print(" MINZ: "); Serial.print(min_accel_x);
        myFile.print(" MINX: "); myFile.print(min_accel_z);
        myFile.print(" MINY: "); myFile.print(min_accel_y);
        myFile.print(" MINZ: "); myFile.print(min_accel_x);
        
        Serial.print(" MAXX: "); Serial.print(max_accel_z);
        Serial.print(" MAXY: "); Serial.print(max_accel_y);
        Serial.print(" MAXZ: "); Serial.print(max_accel_x);
        myFile.print(" MAXX: "); myFile.print(max_accel_z);
        myFile.print(" MAXY: "); myFile.print(max_accel_y);
        myFile.print(" MAXZ: "); myFile.print(max_accel_x);
        
      }
      else if (down_direction == 1){ //Y is Down
        Serial.print(" MINX: "); Serial.print(min_accel_x);
        Serial.print(" MINY: "); Serial.print(min_accel_z);
        Serial.print(" MINZ: "); Serial.print(min_accel_y);
        myFile.print(" MINX: "); myFile.print(min_accel_x);
        myFile.print(" MINY: "); myFile.print(min_accel_z);
        myFile.print(" MINZ: "); myFile.print(min_accel_y);
        
        Serial.print(" MAXX: "); Serial.print(max_accel_x);
        Serial.print(" MAXY: "); Serial.print(max_accel_z);
        Serial.print(" MAXZ: "); Serial.print(max_accel_y);
        myFile.print(" MAXX: "); myFile.print(max_accel_x);
        myFile.print(" MAXY: "); myFile.print(max_accel_z);
        myFile.print(" MAXZ: "); myFile.print(max_accel_y);
        
      }
      else if (down_direction == 2){ //Z is down
        Serial.print(" MINX: "); Serial.print(min_accel_x);
        Serial.print(" MINY: "); Serial.print(min_accel_y);
        Serial.print(" MINZ: "); Serial.print(min_accel_z);
        myFile.print(" MINX: "); myFile.print(min_accel_x);
        myFile.print(" MINY: "); myFile.print(min_accel_y);
        myFile.print(" MINZ: "); myFile.print(min_accel_z);
        
        Serial.print(" MAXX: "); Serial.print(max_accel_x);
        Serial.print(" MAXY: "); Serial.print(max_accel_y);
        Serial.print(" MAXZ: "); Serial.print(max_accel_z);
        myFile.print(" MAXX: "); myFile.print(max_accel_x);
        myFile.print(" MAXY: "); myFile.print(max_accel_y);
        myFile.print(" MAXZ: "); myFile.print(max_accel_z);
        

      }

}


void displayInfo()
{
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  //Output MAX Accel
  if (max_accel_x < a.acceleration.x){
    max_accel_x = a.acceleration.x;
  } 
  if (max_accel_y < a.acceleration.y){ //do this for all directions
    max_accel_y = a.acceleration.y;}
    
  if (max_accel_z < a.acceleration.z){ //do this for all directions
    max_accel_z = a.acceleration.z;}
  
  //Output MIN Accel
  if (min_accel_x > a.acceleration.x){
    min_accel_x = a.acceleration.x;
  } 
  if (min_accel_y > a.acceleration.y){ //do this for all directions
    min_accel_y = a.acceleration.y;}
    
  if (min_accel_z > a.acceleration.z){ //do this for all directions
    min_accel_z = a.acceleration.z;}
    

  count = count + 1;
  //if (count == 5){
  if (last_sec != gps.time.second()){
    count = 0;
    if (gps.date.isValid() && gps.time.isValid() && gps.location.isValid()){
      digitalWrite(ledPin, HIGH);
      print_date();
      print_time();
      print_accel();
      print_latlong();
      
      max_accel_x = a.acceleration.x;
      max_accel_y = a.acceleration.y;
      max_accel_z = a.acceleration.z;

      min_accel_x = a.acceleration.x;
      min_accel_y = a.acceleration.y;
      min_accel_z = a.acceleration.z;

      last_sec = gps.time.second();
      
      Serial.println();
      myFile.println();
      
      myFile.close();
      myFile = SD.open(filename, FILE_WRITE);
    }else{
      Serial.println("INVALID: DATE || TIME || LOCATION");
      digitalWrite(ledPin, LOW);
    }
  }
  
  delay(100); // waits for a second (1000)
}
