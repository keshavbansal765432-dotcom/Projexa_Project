import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'skin_analysis.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            uid TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_path TEXT,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def save_user(email, uid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, uid) VALUES (?, ?)', (email, uid))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def save_result(user_email, image_path, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (user_email,))
    user = cursor.fetchone()
    if user:
        cursor.execute('INSERT INTO analysis_results (user_id, image_path, result) VALUES (?, ?, ?)',
                       (user[0], image_path, result))
        conn.commit()
    conn.close()
