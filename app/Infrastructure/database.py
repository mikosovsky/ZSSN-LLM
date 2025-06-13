import sqlite3
import json
import base64
import io
from datetime import datetime

class Database:
    def __init__(self, db_path="/app/data/chat_history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            # Create chat_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    messages TEXT,
                    timestamp DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            # create files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_history_id INTEGER,
                    file_name TEXT NOT NULL,
                    file_data BLOB,
                    FOREIGN KEY (chat_history_id) REFERENCES chat_history (id)
                )
            ''')
            conn.commit()

    def save_chat_history(self, user_id, messages):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Save chat message
            cursor.execute(
                "INSERT INTO chat_history (user_id, messages, timestamp) VALUES (?, ?, ?)",
                (user_id, json.dumps([{k: v for k, v in msg.items() if k != 'files'} for msg in messages]), datetime.now())
            )
            chat_history_id = cursor.lastrowid
            
            # Save only user uploaded files (not assistant responses)
            for message in messages:
                if message.get("files") and message["role"] == "user":
                    for file in message["files"]:
                        if hasattr(file["data"], "read"):
                            file_content = file["data"].read()
                        else:
                            file_content = file["data"].getvalue()
                            
                        cursor.execute(
                            "INSERT INTO files (chat_history_id, file_name, file_data) VALUES (?, ?, ?)",
                            (chat_history_id, file["name"], file_content)
                        )
            conn.commit()

    def get_chat_history(self, user_id, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get chat messages with their IDs
            cursor.execute("""
                SELECT ch.id, ch.messages, ch.timestamp 
                FROM chat_history ch 
                WHERE ch.user_id = ? 
                ORDER BY ch.timestamp DESC LIMIT ?
            """, (user_id, limit))
            
            chat_history = []
            for chat_id, messages, timestamp in cursor.fetchall():
                messages_dict = json.loads(messages)
                
                # Get files for this chat and associate them only with user messages
                cursor.execute(
                    "SELECT file_name, file_data FROM files WHERE chat_history_id = ?",
                    (chat_id,)
                )
                
                files_data = cursor.fetchall()
                if files_data:
                    for message in messages_dict:
                        if message["role"] == "user":  # Only attach files to user messages
                            message["files"] = [
                                {"name": fname, "data": io.BytesIO(fdata)} 
                                for fname, fdata in files_data
                            ]
                        else:
                            message["files"] = []  # Ensure assistant messages have empty files list
                
                chat_history.append((messages_dict, timestamp))
            
            return chat_history