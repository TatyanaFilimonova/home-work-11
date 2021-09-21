from pymongo import MongoClient
import os

MONGO_DB = os.environ.get('MONGOBD_HOST', "localhost")
client = MongoClient('mongodb://'+MONGO_DB+':27017/')
db = client.contact_book
contact_db = db.contact
counter_db = db.counter
user_db = db.user_
note_db = db.note
