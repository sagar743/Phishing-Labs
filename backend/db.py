import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, '..', 'database')
DB_PATH = os.path.join(DATABASE_DIR, 'database.db')


def get_connection():
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            prediction TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_scan(url, prediction, risk_score, confidence):
    conn = get_connection()
    conn.execute(
        'INSERT INTO scans (url, prediction, risk_score, confidence, timestamp) VALUES (?, ?, ?, ?, ?)',
        (url, prediction, risk_score, confidence, datetime.now().isoformat(timespec='seconds'))
    )
    conn.commit()
    conn.close()


def get_recent_scans(limit=20):
    conn = get_connection()
    rows = conn.execute(
        'SELECT url, prediction, risk_score, confidence, timestamp FROM scans ORDER BY id DESC LIMIT ?',
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
