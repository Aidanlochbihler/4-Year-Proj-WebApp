setlocal
path=C:\Users\Andrew\Documents\code\scheduler\src;%path%



call C:/Users/Andrew/Documents/code/scheduler/dev/env/Scripts/activate.bat 
call cd C:\Users\Andrew\Documents\code\scheduler
call pyinstaller -c -F C:\Users\Andrew\Documents\code\scheduler\main.py

endlocal