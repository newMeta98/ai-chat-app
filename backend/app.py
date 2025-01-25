from flask import Flask, request, jsonify, session
from flask_cors import CORS
from models.user import User
from models.message import class_Message
from models.extracted_info import extracted_info
from models.crud import create_user, get_user_data
from utils.helpers import user_message_explanation, user_data_extraction
from utils.api_client import generate_responseLLM
from utils.memory import memory
from routes.database_routes import database_bp
from routes.auth_routes import auth_bp
from dotenv import load_dotenv
import threading
import os
import sqlite3

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

app.secret_key = os.getenv('SECRET_KEY')

# Register the database and auth routes blueprints
app.register_blueprint(database_bp)
app.register_blueprint(auth_bp)

# Database setup
conn = sqlite3.connect('aigirl.db', check_same_thread=False)
c = conn.cursor()

# Ensure tables exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT, message_type TEXT, timestamp DATETIME, FOREIGN KEY(user_id) REFERENCES users(id))''')
conn.commit()

print("Database initialized")

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    print(f"User message: {user_message}")

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    context = memory.get_context()

    # If context is insufficient, fetch from database
    if len(context) < 5:
        additional_context = class_Message.get_messages_json(user_id, limit=10)
        context = additional_context + context
    
    # Short term memory of message_explanation
    history_explan_mgs = memory.get_explan_mgs()
    message_explanation = user_message_explanation(user_message, context, history_explan_mgs)
    memory.add_explan_mgs(message_explanation)


    # User data extraction from db
    user_data = session.get('user_data')
    if not user_data:
        user_data = get_user_data(user_id)
        if not user_data:
            create_user(user_id)
        else:
            session['user_data'] = user_data


    # User data extraction from db
    user_data = user_data_extraction(user_message, context, user_data)
    print(f"user_data_extraction: {user_data}")

    # Save user message to database
    class_Message.create(user_id, user_message, 'user')
    # Add user message to memory
    memory.add_user_message(user_message)
    # Generate AI response
    response = generate_responseLLM(user_message, user_id, user_data, context, message_explanation)
    print(f"AI response: {response}")

    # Save AI response to database
    class_Message.create(user_id, response, 'ai')
    # Extract information from the message
    threading.Thread(target=extracted_info, args=(user_message, user_id, context, message_explanation)).start()

    # Add AI message to memory
    memory.add_ai_message(response)

    return jsonify({"response": response})

def update_session_user_data(user_id):
    with app.app_context():
        with app.test_request_context('/'):
            session['user_data'] = get_user_data(user_id)
            app.preprocess_request()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
