# backend/models/crud.py
from models.database import get_collection
from bson.objectid import ObjectId
from datetime import datetime

def create_user(user_id):
    user_collection = get_collection(user_id, 'users')
    user_data = {
        "_id": user_id,
        "personal_information": {},
        "professional_information": {},
        "lifestyle": {},
        "social_interactions": {},
        "preferences": {},
        "goals_and_aspirations": {},
        "conversations_and_interactions": {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    user_collection.insert_one(user_data)
    return user_id

def update_personal_information(user_id, data):
    user_collection = get_collection(user_id, 'users')
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"personal_information": data}}
    )
    return True

def update_professional_information(user_id, data):
    user_collection = get_collection(user_id, 'users')
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"professional_information": data}}
    )
    return True

def update_lifestyle(user_id, data):
    user_collection = get_collection(user_id, 'users')
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"lifestyle": data}}
    )
    return True

def update_social_interactions(user_id, data):
    user_collection = get_collection(user_id, 'users')
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"social_interactions": data}}
    )
    return True

def update_preferences(user_id, data):
    user_collection = get_collection(user_id, 'users')
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"preferences": data}}
    )
    return True

def update_goals_and_aspirations(user_id, data):
    user_collection = get_collection(user_id, 'users')
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"goals_and_aspirations": data}}
    )
    return True

def update_conversations_and_interactions(user_id, data):
    user_collection = get_collection(user_id, 'users')
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"conversations_and_interactions": data}}
    )
    return True

def get_user_data(user_id):
    user_collection = get_collection(user_id, 'users')
    return user_collection.find_one({"_id": user_id})
