import sqlite3
import json
from datetime import datetime
import io

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
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_contexts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    context_name TEXT,
                    created_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context_id INTEGER,
                    message_index INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME,
                    FOREIGN KEY (context_id) REFERENCES chat_contexts (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    file_name TEXT NOT NULL,
                    file_data BLOB,
                    FOREIGN KEY (message_id) REFERENCES chat_history (id)
                )
            ''')
            conn.commit()

    def save_chat_history(self, user_id, messages):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_id, messages, timestamp) VALUES (?, ?, ?)",
                (user_id, json.dumps(messages), datetime.now())
            )
            conn.commit()

    def get_chat_history(self, user_id, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT messages, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            return [(json.loads(messages), timestamp) for messages, timestamp in cursor.fetchall()]

    def create_chat_context(self, user_id, context_name=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            context_name = context_name or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            cursor.execute(
                "INSERT INTO chat_contexts (user_id, context_name, created_at) VALUES (?, ?, ?)",
                (user_id, context_name, datetime.now())
            )
            return cursor.lastrowid

    def save_message(self, context_id, role, content, files=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO chat_history 
                   (context_id, message_index, role, content, timestamp) 
                   VALUES (?, (SELECT COALESCE(MAX(message_index) + 1, 0) 
                              FROM chat_history WHERE context_id = ?), ?, ?, ?)""",
                (context_id, context_id, role, content, datetime.now())
            )
            message_id = cursor.lastrowid
            
            if files:
                for file in files:
                    file_content = file["data"].read() if hasattr(file["data"], "read") else file["data"].getvalue()
                    cursor.execute(
                        "INSERT INTO files (message_id, file_name, file_data) VALUES (?, ?, ?)",
                        (message_id, file["name"], file_content)
                    )
            conn.commit()
            return message_id

    def get_chat_contexts(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, context_name, created_at 
                   FROM chat_contexts 
                   WHERE user_id = ? 
                   ORDER BY created_at DESC""",
                (user_id,)
            )
            return cursor.fetchall()

    def get_context_messages(self, context_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT h.id, h.role, h.content, h.timestamp,
                          GROUP_CONCAT(json_object('name', f.file_name, 
                                                 'data', f.file_data)) as files
                   FROM chat_history h
                   LEFT JOIN files f ON h.id = f.message_id
                   WHERE h.context_id = ?
                   GROUP BY h.id
                   ORDER BY h.message_index""",
                (context_id,)
            )
            messages = []
            for msg_id, role, content, timestamp, files_json in cursor.fetchall():
                msg = {"role": role, "content": content, "timestamp": timestamp}
                if files_json:
                    files_data = json.loads(f"[{files_json}]")
                    msg["files"] = [{
                        "name": f["name"],
                        "data": io.BytesIO(f["data"])
                    } for f in files_data]
                else:
                    msg["files"] = []
                messages.append(msg)
            return messages