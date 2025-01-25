# backend/utils/database.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('aigirl.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
