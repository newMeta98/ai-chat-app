# backend/models/user.py
from utils.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    @staticmethod
    def create(name, email, password):
        conn = get_db_connection()
        c = conn.cursor()
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return User(user_id, name, email, hashed_password)

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row['id'], row['name'], row['email'], row['password'])
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row['id'], row['name'], row['email'], row['password'])
        return None

    def check_password(self, password):
        return check_password_hash(self.password, password)
