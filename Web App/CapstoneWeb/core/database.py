from pymongo import MongoClient
client = MongoClient('localhost', 27017)
data_db = client['data']
trip_col = data_db['trip']
django_db = client['django']