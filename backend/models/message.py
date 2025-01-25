# backend/models/message.py
from utils.database import get_db_connection
import logging
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class class_Message:
    def __init__(self, id, user_id, content, message_type, timestamp):
        self.id = id
        self.user_id = user_id
        self.content = content
        self.message_type = message_type
        self.timestamp = timestamp
    

    def to_dict(self):
        # Convert timestamp to ISO format string if it's a datetime object
        if isinstance(self.timestamp, datetime.datetime):
            timestamp_str = self.timestamp.isoformat()
        else:
            timestamp_str = self.timestamp

        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": timestamp_str
        }

    @staticmethod
    def create(user_id, content, message_type):
        timestamp = datetime.datetime.now()
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO messages (user_id, content, message_type, timestamp) VALUES (?, ?, ?, ?)", (user_id, content, message_type, timestamp))
            conn.commit()
            message_id = c.lastrowid
            logger.info(f"Message created: id={message_id}, user_id={user_id}")
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
        return class_Message(message_id, user_id, content, message_type, timestamp)
    
    @staticmethod
    def get_by_user_id(user_id, limit=20):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
            rows = c.fetchall()
            conn.close()
            messages = []
            for row in rows:
                messages.append(class_Message(row['id'], row['user_id'], row['content'], row['message_type'], row['timestamp']))
            return messages
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            raise

    @staticmethod
    def get_messages_json(user_id, limit=20):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("SELECT content, message_type FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit))
            rows = c.fetchall()
            conn.close()
            messages = []
            for row in rows:
                message = {
                    "sender": row['message_type'],
                    "content": row['content']     
                }
                messages.append(message)
            # Reverse the order to get messages from oldest to newest
            messages.reverse()
            return messages
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            raise