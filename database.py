# database.py
import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name="cv_database.db"):
        self.db_name = db_name
        self.setup_database()

    def setup_database(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                cv_text TEXT,
                upload_date TIMESTAMP,
                parsed_data TEXT
            )''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                requirements TEXT,
                created_date TIMESTAMP
            )''')

            conn.commit()

    def insert_candidate(self, name, email, phone, cv_text, parsed_data):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO candidates (name, email, phone, cv_text, upload_date, parsed_data)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, phone, cv_text, datetime.now(), parsed_data))
            return cursor.lastrowid

    def update_candidate(self, id, name, email, phone, parsed_data):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE candidates 
            SET name=?, email=?, phone=?, parsed_data=?
            WHERE id=?
            ''', (name, email, phone, parsed_data, id))
            return cursor.rowcount > 0

    def delete_candidate(self, id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM candidates WHERE id=?', (id,))
            return cursor.rowcount > 0

    def get_candidate(self, id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM candidates WHERE id=?', (id,))
            return cursor.fetchone()

    def insert_job_template(self, title, description, requirements):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO job_templates (title, description, requirements, created_date)
            VALUES (?, ?, ?, ?)
            ''', (title, description, requirements, datetime.now()))
            return cursor.lastrowid

    def update_job_template(self, id, title, description, requirements):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE job_templates 
            SET title=?, description=?, requirements=?
            WHERE id=?
            ''', (title, description, requirements, id))
            return cursor.rowcount > 0

    def delete_job_template(self, id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM job_templates WHERE id=?', (id,))
            return cursor.rowcount > 0

    def get_job_template(self, id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM job_templates WHERE id=?', (id,))
            return cursor.fetchone()

    def get_all_candidates(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM candidates')
            return cursor.fetchall()

    def get_all_job_templates(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM job_templates')
            return cursor.fetchall()