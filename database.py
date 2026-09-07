import sqlite3
import os

DB_NAME = "news.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute("PRAGMA encoding = 'UTF-8';")
    return conn, cursor

def init_db():
    conn, cursor = get_db_connection()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            published_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("تم إنشاء قاعدة البيانات بنجاح وبترميز UTF-8.")