from flask import Blueprint, request, jsonify, session
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"Received data: {data}")  # Add this line for debugging
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Invalid request data"}), 400

    email = data['email']
    password = data['password']
    user = User.get_by_email(email)
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        print(f"Session data after login: {session}")  # Add this line for debugging
        return jsonify({"message": "Login successful", "user_id": user.id, "user_name": user.name})
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Invalid request data"}), 400

    name = data['name']
    email = data['email']
    password = data['password']
    if User.get_by_email(email):
        return jsonify({"error": "Email already exists"}), 400
    else:
        user = User.create(name, email, password)
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({"message": "Account created successfully", "user_id": user.id, "user_name": user.name})

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({"message": "Logout successful"})
