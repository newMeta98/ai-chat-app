#backend/routes/database_routes.py


from flask import Blueprint, request, jsonify, render_template_string
from models.crud import create_user, get_user_data
import sqlite3

database_bp = Blueprint('database', __name__)

@database_bp.route('/view_database', methods=['GET'])
def view_database():
    conn = sqlite3.connect('aigirl.db', check_same_thread=False)
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    users = c.fetchall()

    c.execute("SELECT * FROM messages")
    messages = c.fetchall()

    conn.close()

    return render_template_string('''
        <h1>Users Table</h1>
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Name</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user[0] }}</td>
                <td>{{ user[1] }}</td>
            </tr>
            {% endfor %}
        </table>

        <h1>Messages Table</h1>
        <table border="1">
            <tr>
                <th>ID</th>
                <th>User ID</th>
                <th>Content</th>
            </tr>
            {% for message in messages %}
            <tr>
                <td>{{ message[0] }}</td>
                <td>{{ message[1] }}</td>
                <td>{{ message[2] }}</td>
            </tr>
            {% endfor %}
        </table>
    ''', users=users, messages=messages)

@database_bp.route('/api/create_user', methods=['POST'])
def create_user_route():
    user_id = request.json['user_id']
    create_user(user_id)
    return jsonify({"message": "User created successfully"})

@database_bp.route('/api/get_user_data/<user_id>', methods=['GET'])
def get_user_data_route(user_id):
    user_data = get_user_data(user_id)
    return jsonify(user_data)