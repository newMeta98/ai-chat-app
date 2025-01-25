# backend/models/extracted_info.py
import re
import os
import json
import logging
from openai import OpenAI
from models.database import get_collection
from flask import session, current_app as app
from utils.memory import memory
from models.message import class_Message

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extracted_info(user_message, user_id, context, message_explanation):
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("OpenAI API key not set.")
        return []
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    user_data = get_user_data(user_id)
    print(f"user_data:{user_data}\n")
    # Third LLM: Extract new data
    output_instruction = """Output instruction: 1. Basic Personal Information User Message: "Hi, I'm John Doe. I was born on May 15, 1990, and I'm single. I live at 123 Main St, Anytown, USA." Extracted Information: { "personal_information": { "basic_info": { "full_name": "John Doe", "date_of_birth": "1990-05-15", "gender": "male", "marital_status": "single", "nationality": "American" }, "contact_info": { "addresses": [ { "type": "home", "street": "123 Main St", "city": "Anytown", "country": "USA" } ] } } } 2. Professional Information (Job) User Message: "I work as a Software Engineer at TechCorp. I started there on January 1, 2019, and my responsibilities include developing software and leading projects. My salary is $80,000." Extracted Information: { "professional_information": { "jobs": [ { "_id": "job1", "title": "Software Engineer", "company": "TechCorp", "start_date": "2019-01-01", "end_date": null, "responsibilities": ["Develop software", "Lead projects"], "salary": 80000, "department": "Engineering" } ] } } 3. Professional Information (Education) User Message: "I have a Bachelor of Science in Computer Science from the University of Tech. I graduated in May 2018 with a GPA of 3.8 and Summa Cum Laude honors." Extracted Information: { "professional_information": { "education": [ { "_id": "education1", "degree": "Bachelor of Science", "major": "Computer Science", "institution": "University of Tech", "graduation_date": "2018-05-15", "gpa": 3.8, "honors": "Summa Cum Laude" } ] } } 4. Professional Information (Skills) User Message: "I have skills in programming and project management." Extracted Information: { "professional_information": { "skills": ["Programming", "Project Management"] } } 5. Lifestyle (Hobbies) User Message: "I enjoy photography and go out weekly to take pictures. I use a camera and a lens. My favorite genre is landscape." Extracted Information: { "lifestyle": { "hobbies": [ { "_id": "hobby1", "name": "Photography", "frequency": "weekly", "skill_level": "advanced", "equipment": ["camera", "lens"], "favorite_genre": "landscape" } ] } } 6. Lifestyle (Health) User Message: "I have allergies to peanuts and my fitness goal is to lose weight. I exercise 5 days a week and follow a gluten-free diet." Extracted Information: { "lifestyle": { "health": { "medical_history": ["allergies"], "allergies": ["peanuts"], "fitness_goals": ["lose_weight"], "exercise_routine": "5 days a week", "dietary_restrictions": ["gluten-free"] } } } 7. Lifestyle (Financial) User Message: "My income is $90,000 and I have $60,000 in expenses. I have $20,000 in savings and $15,000 invested in stocks. I bank with National Bank." Extracted Information: { "lifestyle": { "financial": { "income": 90000, "expenses": 60000, "savings": 20000, "investments": [ { "_id": "inv1", "type": "stocks", "value": 15000 } ], "bank": "National Bank" } } } 8. Lifestyle (Travel) User Message: "I am planning a trip to Paris, France on March 10, 2024. It's for a vacation and I will be staying at Hotel Lux." Extracted Information: { "lifestyle": { "travel": [ { "_id": "travel1", "destination": "Paris, France", "travel_date": "2024-03-10", "purpose": "vacation", "accommodation": "Hotel Lux" } ] } } 9. Social Interactions (Contacts) User Message: "My sister Jane Doe is a teacher. Her email is janedoe@example.com and her phone number is +1234567890. She loves cats and enjoys hiking. Her birthday is on May 15, 1995." Extracted Information: { "social_interactions": { "contacts": [ { "_id": "contact001", "types": ["family", "friend"], "name": "Jane Doe", "relationship": "sister", "contact_info": { "email": "janedoe@example.com", "phone": "+1234567890" }, "birthday": "1995-05-15", "occupation": "Teacher", "liking_scale": 3, "interests": ["reading", "traveling"], "notes": "Loves cats and enjoys hiking." } ] } } 10. Social Interactions (Events) User Message: "I have a wedding coming up on June 15, 2024, at the Grand Hotel in Cityville. It's a one-time event." Extracted Information: { "social_interactions": { "events": [ { "_id": "event1", "type": "wedding", "date": "2024-06-15", "location": "Grand Hotel, Cityville, USA", "description": "Sister's wedding", "participants": ["family1", "friend1"], "recurring": false } ] } } 11. Preferences (Communication) User Message: "I prefer to communicate via text in the evening." Extracted Information: { "preferences": { "communication": { "preferred_channel": "text", "preferred_time": "evening" } } } 12. Preferences (Cultural) User Message: "I enjoy watching action and sci-fi movies. My favorite artists are Artist A and Artist B." Extracted Information: { "preferences": { "cultural": { "movies": ["action", "sci-fi"], "favorite_artists": ["Artist A", "Artist B"] } } } 13. Preferences (Technology) User Message: "I use Google Maps and Spotify regularly." Extracted Information: { "preferences": { "technology": { "preferred_apps": ["Google Maps", "Spotify"] } } } 14. Goals and Aspirations (Personal Goals) User Message: "My goal is to learn Spanish by the end of this year." Extracted Information: { "goals_and_aspirations": { "personal_goals": [ { "_id": "goal1", "description": "Learn a new language", "target_date": "2023-12-31", "progress": 50, "language": "Spanish" } ] } } 15. Goals and Aspirations (Professional Goals) User Message: "I want to advance to a managerial position by the end of 2025." Extracted Information: { "goals_and_aspirations": { "professional_goals": [ { "_id": "goal2", "description": "Advance to a managerial position", "target_date": "2025-12-31", "progress": 30 } ] } } 16. Conversations and Interactions (Conversations) User Message: "We discussed project timelines and deliverables today. The conversation was positive and focused on deadlines and project management." Extracted Information: { "conversations_and_interactions": { "conversations": [ { "_id": "conv001", "date": "2023-10-01", "topic": "Project Deadlines", "summary": "Discussed project timelines and deliverables", "sentiment": "positive", "keywords": ["deadline", "project"] } ] } } 17. Conversations and Interactions (Feedback) User Message: "I received great service today. I would rate it 4 out of 5." Extracted Information: { "conversations_and_interactions": { "feedback": [ { "_id": "feedback1", "date": "2023-10-01", "rating": 4, "comment": "Great service!" } ] } }"""
    about_db = """# backend/models/crud.py;from models.database import get_collection;from bson.objectid import ObjectId;from datetime import datetime;def create_user(user_id):;user_collection = get_collection(user_id, 'users');user_data = {"_id": user_id,"personal_information": {},"professional_information": {},"lifestyle": {},"social_interactions": {},"preferences": {},"goals_and_aspirations": {},"conversations_and_interactions": {},"created_at": datetime.now(),"updated_at": datetime.now()};user_collection.insert_one(user_data);return user_id;def update_personal_information(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": {"personal_information": data}});return True;def update_professional_information(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": {"professional_information": data}});return True;def update_lifestyle(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": {"lifestyle": data}});return True;def update_social_interactions(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": {"social_interactions": data}});return True;def update_preferences(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": {"preferences": data}});return True;def update_goals_and_aspirations(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": {"goals_and_aspirations": data}});return True;def update_conversations_and_interactions(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": {"conversations_and_interactions": data}});return True;def get_user_data(user_id):;user_collection = get_collection(user_id, 'users');return user_collection.find_one({"_id": user_id});# backend/models/database.py;from pymongo import MongoClient;import os;def get_client():;mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/');return MongoClient(mongo_uri);def get_db(user_id):;client = get_client();db_name = f'aigirl_{user_id}';return client[db_name];def get_collection(user_id, collection_name):;db = get_db(user_id);return db[collection_name];#about_output;extracted_info_data = json.loads(extracted_info_response);update_user_data(user_id, extracted_info_data);return extracted_info_data;except json.JSONDecodeError:;print("Invalid JSON response from LLM.");return [];return [];def update_user_data(user_id, data):;user_collection = get_collection(user_id, 'users');user_collection.update_one({"_id": user_id},{"$set": data});return True;def get_user_data(user_id):;user_collection = get_collection(user_id, 'users');return user_collection.find_one({"_id": user_id})"""
    example_schema = """{"_id": "user_id","personal_information": {"basic_info": {"full_name": "John Doe","date_of_birth": "1990-05-15","gender": "male","marital_status": "single","nationality": "American"},"contact_info": {"emails": ["johndoe@example.com"],"phones": ["+1234567890"],"addresses": [{"type": "home","street": "123 Main St","city": "Anytown","country": "USA"}],"social_media": {"facebook": "johndoe","twitter": "johndoe","instagram": "johndoe"}},"demographics": {"income_range": "50k-100k","education_level": "Bachelor's Degree","employment_status": "employed"}},"professional_information": {"jobs": [{"_id": "job1","title": "Software Engineer","company": "TechCorp","start_date": "2019-01-01","end_date": "2023-12-31","responsibilities": ["Develop software", "Lead projects"],"salary": 80000,"department": "Engineering"}],"education": [{"_id": "education1","degree": "Bachelor of Science","major": "Computer Science","institution": "University of Tech","graduation_date": "2018-05-15","gpa": 3.8,"honors": "Summa Cum Laude"}],"skills": ["Programming", "Project Management"]},"lifestyle": {"hobbies": [{"_id": "hobby1","name": "Photography","frequency": "weekly","skill_level": "advanced","equipment": ["camera", "lens"],"favorite_genre": "landscape"}],"health": {"medical_history": ["allergies"],"allergies": ["peanuts"],"fitness_goals": ["lose_weight"],"exercise_routine": "5 days a week","dietary_restrictions": ["gluten-free"]},"financial": {"income": 90000,"expenses": 60000,"savings": 20000,"investments": [{"_id": "inv1","type": "stocks","value": 15000}],"bank": "National Bank"},"travel": [{"_id": "travel1","destination": "Paris, France","travel_date": "2024-03-10","purpose": "vacation","accommodation": "Hotel Lux"}]},"social_interactions": {"contacts": [{"id": "contact001","types": ["family", "friend"],"name": "Jane Doe","relationship": "sister","contact_info": {"email": "janedoe@example.com","phone": "+1234567890"},"birthday": "1995-05-15","occupation": "Teacher","liking_scale": 3,"interests": ["reading", "traveling"],"notes": "Loves cats and enjoys hiking."},{"id": "contact002","types": ["colleague"],"name": "Bob Johnson","relationship": "work colleague","contact_info": {"email": "bobjohnson@example.com","phone": "+1122334455"},"birthday": "1985-03-12","occupation": "Engineer","liking_scale": 0,"interests": ["gaming", "coding"],"notes": "Enjoys programming and competitive gaming."},{"id": "contact003","types": ["acquaintance"],"name": "Charlie Brown","relationship": "neighbor","contact_info": {"email": "charliebrown@example.com","phone": "+2233445566"},"birthday": "1980-07-30","occupation": "Artist","liking_scale": -1,"interests": ["painting", "music"],"notes": "Sometimes hosts local art exhibitions."}],"events": [{"_id": "event1","type": "wedding","date": "2024-06-15","location": "Grand Hotel, Cityville, USA","description": "Sister's wedding","participants": ["family1", "friend1"],"recurring": false}]},"preferences": {"communication": {"preferred_channel": "text","preferred_time": "evening"},"cultural": {"movies": ["action", "sci-fi"],"music": ["rock", "jazz"],"books": ["fiction", "mystery"],"favorite_artists": ["Artist A", "Artist B"],"favorite_movies": ["Inception", "Interstellar"]},"technology": {"preferred_apps": ["Google Maps", "Spotify"],"devices": ["iPhone", "MacBook"]}},"goals_and_aspirations": {"personal_goals": [{"_id": "goal1","description": "Learn a new language","target_date": "2024-12-31","progress": 50,"language": "Spanish"}],"professional_goals": [{"_id": "goal2","description": "Advance to a managerial position","target_date": "2025-12-31","progress": 30}]},"conversations_and_interactions": {"conversations": [{"_id": "conv001","date": "2023-10-01","topic": "Project Deadlines","summary": "Discussed project timelines and deliverables","sentiment": "positive","keywords": ["deadline", "project"]}],"feedback": [{"_id": "feedback1","date": "2023-10-01","rating": 4,"comment": "Great service!"}]},"created_at": "2023-09-01","updated_at": "2023-09-15"}"""
    useful_information = "User's Person Info: First Name, Last Name, nickname, Age, Gender, nationality... . Names of People Mentioned: Extract names of individuals the user refers to, such as friends, family, or colleagues. Relationships Between People: Understand the nature of relationships, like friends, spouses, or coworkers. Possessions: Identify items the user owns, such as cars, phones, or houses. Memories: Capture significant events or memories the user shares. Family Details: Extract information about the user's family, such as spouses, children, or parents. Job Details: Gather information about the user's current or past jobs, including job titles and companies. Education Details: Note the user's educational background, including schools attended and degrees earned. Hobbies and Interests: Identify the user's hobbies, interests, and passions. Skills and Expertise: Recognize the user's skills, both professional and personal. Preferences and Dislikes: Understand the user's preferences, such as favorite foods or dislikes, such as certain types of food. Financial Information: Extract financial details, such as income, expenses, or investment goals. Health Information: Capture health-related information, such as medical conditions or fitness goals. Travel Plans: Identify travel plans, including destinations and dates. Technologies Used: Note the technologies or devices the user mentions. Communication Preferences: Understand how the user prefers to communicate, such as email or phone. Social Media Handles: Capture social media usernames if mentioned. Dietary Preferences: Identify dietary preferences, such as being vegetarian or having food allergies. Languages Spoken: Note languages the user speaks or prefers. Religious and Spiritual Beliefs: Capture religious or spiritual beliefs if shared. Cultural Background: Understand the user's cultural background or heritage. Legal Information: Extract legal details, such as citizenship or legal issues. Personal Goals and Aspirations: Identify the user's personal or professional goals. Emotional State: Recognize the user's current emotional state or mood. Mental Health Information: Capture any mental health-related information shared. Security Preferences: Note preferences related to security, such as authentication methods. Legal Status: Understand the user's legal status, such as marital or employment status. Clothing Preferences: Identify clothing preferences or brand loyalty. Musical Preferences: Note musical preferences, such as favorite genres or artists. Literary Preferences: Capture literary preferences, such as favorite books or authors. Cinematic Preferences: Identify cinematic preferences, such as favorite movies or directors. Technological Preferences: Note technological preferences, such as preferred brands or software. Educational Preferences: Understand the user's preferred learning methods or educational interests. Professional Associations: Identify professional organizations or memberships. Legal Issues: Capture any legal problems or concerns the user mentions. Past Experiences: Note significant past experiences, such as previous jobs or education. Financial Goals: Understand the user's financial goals or plans. Educational Achievements: Capture educational achievements, such as degrees or certifications. Professional Achievements: Note professional achievements, such as awards or publications. Travel Experiences: Identify places the user has traveled to or favorite destinations. Culinary Preferences: Capture culinary preferences, such as favorite cuisines or restaurants. Artistic Preferences: Note artistic preferences, such as favorite art styles or artists. Technological Expertise: Identify the user's expertise in specific technologies or tools. Communication Styles: Understand the user's preferred communication style or tone. Cognitive Preferences: Note cognitive preferences, such as learning styles or thinking patterns. Emotional Preferences: Capture how the user prefers to express or handle emotions. Social Preferences: Identify social preferences, such as being extroverted or introverted. Psychological Preferences: Note psychological preferences or personality types. Spiritual Preferences: Capture spiritual practices or beliefs. Lifestyle Choices: Understand the user's lifestyle choices, such as daily routines or hobbies. Environmental Preferences: Note environmental concerns or actions the user takes. Ethical Preferences: Identify the user's ethical beliefs or standards. Philosophical Preferences: Capture philosophical beliefs or thinkers the user admires. Aesthetic Preferences: Note aesthetic preferences, such as favorite colors or design styles. Other Miscellaneous Information: Capture any other relevant information that doesn't fit into the above categories."
    output_instruction_database = """Output instruction: 1. extracted_main_obj: "personal_information", Extracted Information {"personal_information": {"basic_info": {"full_name": "John Doe","date_of_birth": "1990-05-15","gender": "male","marital_status": "single","nationality": "American"},"contact_info": {"emails": ["johndoe@example.com"],"phones": ["+1234567890"],"addresses": [{"type": "home","street": "123 Main St","city": "Anytown","country": "USA"}],"social_media": {"facebook": "johndoe","twitter": "johndoe","instagram": "johndoe"}},"demographics": {"income_range": "50k-100k","education_level": "Bachelor's Degree","employment_status": "employed"}},"professional_information": {"jobs": [{"_id": "job1","title": "Software Engineer","company": "TechCorp","start_date": "2019-01-01","end_date": "2023-12-31","responsibilities": ["Develop software", "Lead projects"],"salary": 80000,"department": "Engineering"}],"education": [{"_id": "education1","degree": "Bachelor of Science","major": "Computer Science","institution": "University of Tech","graduation_date": "2018-05-15","gpa": 3.8,"honors": "Summa Cum Laude"}],"skills": ["Programming", "Project Management"]}}. 2. extracted_main_obj: "lifestyle", Extracted Information {"lifestyle": {"hobbies": [{"_id": "hobby1","name": "Photography","frequency": "weekly","skill_level": "advanced","equipment": ["camera", "lens"],"favorite_genre": "landscape"}],"health": {"medical_history": ["allergies"],"allergies": ["peanuts"],"fitness_goals": ["lose_weight"],"exercise_routine": "5 days a week","dietary_restrictions": ["gluten-free"]},"financial": {"income": 90000,"expenses": 60000,"savings": 20000,"investments": [{"_id": "inv1","type": "stocks","value": 15000}],"bank": "National Bank"},"travel": [{"_id": "travel1","destination": "Paris, France","travel_date": "2024-03-10","purpose": "vacation","accommodation": "Hotel Lux"}]}}. 3. extracted_main_obj: "social_interactions", Extracted Information"social_interactions": {"contacts": [{"id": "contact001","types": ["family", "friend"],"name": "Jane Doe","relationship": "sister","contact_info": {"email": "janedoe@example.com","phone": "+1234567890"},"birthday": "1995-05-15","occupation": "Teacher","liking_scale": 3,"interests": ["reading", "traveling"],"notes": "Loves cats and enjoys hiking."},{"id": "contact002","types": ["colleague"],"name": "Bob Johnson","relationship": "work colleague","contact_info": {"email": "bobjohnson@example.com","phone": "+1122334455"},"birthday": "1985-03-12","occupation": "Engineer","liking_scale": 0,"interests": ["gaming", "coding"],"notes": "Enjoys programming and competitive gaming."},{"id": "contact003","types": ["acquaintance"],"name": "Charlie Brown","relationship": "neighbor","contact_info": {"email": "charliebrown@example.com","phone": "+2233445566"},"birthday": "1980-07-30","occupation": "Artist","liking_scale": -1,"interests": ["painting", "music"],"notes": "Sometimes hosts local art exhibitions."}],"events": [{"_id": "event1","type": "wedding","date": "2024-06-15","location": "Grand Hotel, Cityville, USA","description": "Sister's wedding","participants": ["family1", "friend1"],"recurring": false}]}}. 5. extracted_main_obj:"preferences", Extracted Information"social_interactions": {"preferences": {"communication": {"preferred_channel": "text","preferred_time": "evening"},"cultural": {"movies": ["action", "sci-fi"],"music": ["rock", "jazz"],"books": ["fiction", "mystery"],"favorite_artists": ["Artist A", "Artist B"],"favorite_movies": ["Inception", "Interstellar"]},"technology": {"preferred_apps": ["Google Maps", "Spotify"],"devices": ["iPhone", "MacBook"]}}} 6. extracted_main_obj: "goals_and_aspirations", Extracted Information {"goals_and_aspirations": {"personal_goals": [{"_id": "goal1","description": "Learn a new language","target_date": "2024-12-31","progress": 50,"language": "Spanish"}],"professional_goals": [{"_id": "goal2","description": "Advance to a managerial position","target_date": "2025-12-31","progress": 30}]}. 7. extracted_main_obj: "goals_and_aspirations", Extracted Information {"conversations_and_interactions": {"conversations": [{"_id": "conv001","date": "2023-10-01","topic": "Project Deadlines","summary": "Discussed project timelines and deliverables","sentiment": "positive","keywords": ["deadline", "project"]}],"feedback": [{"_id": "feedback1","date": "2023-10-01","rating": 4,"comment": "Great service!"}]}}"""
    output_instruction_combine = """Output Example: """

    extracted_information = extract_information(user_message, useful_information, about_db, example_schema, output_instruction, context, message_explanation)
    if extracted_information == 'no' or extracted_information == 'extracted_info: no':
            print(extracted_information)
    else:
        print(extracted_information)
        extracted_main_obj = extract_main_obj(extracted_information)
        print(f"extracted_main_obj: {extracted_main_obj}")
        
        extracted_curent_data = extract_curent_data(extracted_main_obj, user_data, output_instruction_database)
        print(f"extracted_curent_data: {extracted_curent_data}")
        
        combined_data = combine_data(extracted_curent_data, extracted_information)
        print(f"combined_data: {combined_data}")
        if extracted_information == 'no':
            print(f"{combined_data}")
        else:
            try:
                extracted_info = re.sub(r'combined_data: \s*', '', combined_data)
                extracted_info = re.sub(r'json\s*', '', extracted_info)
                extracted_info = re.sub(r'```\s*', '', extracted_info)
                print(f"extracted:{extracted_info}")
                extracted_info_data = json.loads(extracted_info)
                print(f"extracted_info:{extracted_info_data}")
                update_user_data(user_id, extracted_info_data)
                return extracted_info_data
            except json.JSONDecodeError:
                print("backend/models/extracted_info.py | Invalid JSON response from LLM.")
                return []
            return []


def update_user_data(user_id, data):
    try:
        user_collection = get_collection(user_id, 'users')
        print(user_collection)
        print(data)
        logger.debug(f"Updating user data for user_id: {user_id}")
        logger.debug(f"Data to be updated: {data}")

        result = user_collection.update_one(
            {"_id": user_id},
            {"$set": data},
            upsert=True  # Ensure the document is created if it doesn't exist
        )

        if result.matched_count:  
            # Update user data in session
            from app import update_session_user_data
            update_session_user_data(user_id)
            logger.info(f"User data updated successfully for user_id: {user_id}")
        else:
            logger.warning(f"No user data found to update for user_id: {user_id}")

        return True
    except Exception as e:
        logger.error(f"Error updating user data for user_id: {user_id}", exc_info=True)
        return False

def get_user_data(user_id):
    user_collection = get_collection(user_id, 'users')
    return user_collection.find_one({"_id": user_id})


def extract_information(user_message, useful_information, about_db, example_schema, output_instruction, context, message_explanation):
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("OpenAI API key not set.")
        return []
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt_1 = (
         "Role: You are a helpful Asistent 'Information Extraction Expert'. You will Extract the new information from the user_message and looking at conversational context and message_explanation so we can add correct data to the database.\n" 
         "Determine if the user message contains any information that should be written to the database. Return: extracted_info: Extracted Information"    
        f"About extracting useful information: [{useful_information}]\n" 
        f"Ccode for db:[{about_db}] and Example Schema json format {example_schema} so you can get a better understanding.\n"
        f"Example's of structures for Extracted Information {output_instruction}."
        f"LOOK AT the conversational context:{context} and message_explanation:{message_explanation}. to better Understand info you are extracting"
         "list of main_Object's: personal_information, professional_information, lifestyle, social_interactions, preferences, goals_and_aspirations, conversations_and_interactions"
         "Determine if the user_message contains any useful information that should be added to the database. Return: extracted_info: Extracted Information or 'no'"
    )

    messages_1 = [
        {"role": "system", "content": system_prompt_1},
        {"role": "user", "content": f"user_message: {user_message}"}
    ]
    response_1 = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages_1,
    )
    extracted_information = response_1.choices[0].message.content.strip()
    return extracted_information

def extract_main_obj(extracted_information):
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("OpenAI API key not set.")
        return []
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    system_prompt_1 = (
         f"Role: You are a helpful Asistent 'Main Object Extraction Expert'. You will Extract the main Object from {extracted_information} based on list of main Object's.\n" 
         "Determine what is the main Object from extracted_information by looking main Object's in list of main Object's. Return: extracted_main_obj: main Object"    
         "here you will find main Object's, list of main Object's: personal_information, professional_information, lifestyle, social_interactions, preferences, goals_and_aspirations, conversations_and_interactions"
         "Determine what is the main Object from extracted_information by looking main Object's in list of main Object's. Return: extracted_main_obj: main Object"
    )

    messages_1 = [
        {"role": "system", "content": system_prompt_1},
        {"role": "user", "content": "Determine what is the main Object from extracted_information by looking main Object's in list of main Object's. Return: extracted_main_obj: main Object"}
    ]
    response_1 = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages_1,
    )
    extract_main_obj = response_1.choices[0].message.content.strip()
    return extract_main_obj

def extract_curent_data(extracted_main_obj, user_data, output_instruction_database):
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("OpenAI API key not set.")
        return []
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    print(f"user_dataDB: {user_data}")
    system_prompt_1 = (
         "Role: You are a helpful Asistent 'Information Extraction Expert'. You will Extract the data of extracted_main_obj (all its childerm) from database in json form. Return: extracted_info_db: Extracted Information\n" 
         "Extract main Object data from database. Return: extracted_info_db: Extracted Information"    
        f"main Object: {extracted_main_obj}.\n" 
        f"database: {user_data}. .\n"
        f"Example's of for Extracted Information {output_instruction_database}."
         "list of main_Object's: personal_information, professional_information, lifestyle, social_interactions, preferences, goals_and_aspirations, conversations_and_interactions"
         "Extract main Object data from database. Return: extracted_info_db: Extracted Information"  
    )

    messages_1 = [
        {"role": "system", "content": system_prompt_1},
        {"role": "user", "content": "Extract main Object data from database. Return: extracted_info_db: Extracted Information"}
    ]
    response_1 = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages_1,
    )
    extracted_info_db = response_1.choices[0].message.content.strip()
    return extracted_info_db

def combine_data(extracted_info_db, extracted_information):

    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("OpenAI API key not set.")
        return []
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    system_prompt_1 = (
         "Role: You are a helpful Asistent 'Data Merge Expert'. You will merge extracted_info_db and extracted_info so we can add it to db. Return: combined_data: Merged data\n"   
        f"{extracted_info_db}.\n" 
        f"{extracted_information}. .\n"
         "Look at extracted_info_db and extracted_info data. Merge extracted_info_db and extracted_info and make sure you dont lose any gata in the process. Return: combined_data: Merged data "  
    )

    messages_1 = [
        {"role": "system", "content": system_prompt_1},
        {"role": "user", "content": "Merge extracted_info_db and extracted_info and make sure you dont lose any gata in the process. Return: combined_data: Merged data"}
    ]
    response_1 = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages_1,
    )
    combined_data = response_1.choices[0].message.content.strip()
    return combined_data