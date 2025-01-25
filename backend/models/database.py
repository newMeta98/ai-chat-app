# backend/models/database.py
from pymongo import MongoClient
import os

def get_client():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    return MongoClient(mongo_uri)

def get_db(user_id):
    client = get_client()
    db_name = f'aigirl_{user_id}'
    return client[db_name]

def get_collection(user_id, collection_name):
    db = get_db(user_id)
    return db[collection_name]

def get_user_data(user_id):
    user_collection = get_collection(user_id, 'users')
    return user_collection.find_one({"_id": user_id})