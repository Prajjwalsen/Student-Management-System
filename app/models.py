# app/models.py
from .database import get_db_connection
from datetime import datetime

class Student:
    def __init__(self, data=None):
        if data:
            self.id = data.get('id')
            self.student_id = data['student_id']
            self.first_name = data['first_name']
            self.last_name = data['last_name']
            self.date_of_birth = data.get('date_of_birth')
            self.email = data.get('email')
            self.phone = data.get('phone')
            self.address = data.get('address')
            self.department = data['department']
            self.enrollment_year = data.get('enrollment_year', datetime.now().year)
            self.course = data['course']
            self.building_block = data['building_block']
            self.semester = data['semester']
            self.cgpa = data['cgpa']
            self.attendance_percentage = data['attendance_percentage']
            self.fees_status = data['fees_status']
            self.created_at = data.get('created_at')
            self.updated_at = data.get('updated_at')

    @staticmethod
    def get_all(page=1, per_page=20, search='', department='', semester=''):
        conn = get_db_connection()
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        if search:
            query += " AND (first_name LIKE ? OR last_name LIKE ? OR student_id LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        if department:
            query += " AND department = ?"
            params.append(department)

        if semester:
            query += " AND semester = ?"
            params.append(semester)

        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Add pagination
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        cursor = conn.execute(query, params)
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return students, total

    @staticmethod
    def get_by_id(student_id):
        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student = cursor.fetchone()
        conn.close()
        return dict(student) if student else None

    @staticmethod
    def create(data):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Generate student ID
        cursor.execute("SELECT student_id FROM students ORDER BY student_id DESC LIMIT 1")
        last_student = cursor.fetchone()
        if last_student:
            last_num = int(last_student['student_id'][1:])
            new_num = last_num + 1
        else:
            new_num = 1
        student_id = f"S{new_num:05d}"

        cursor.execute('''
            INSERT INTO students (
                student_id, first_name, last_name, date_of_birth, email, phone,
                address, department, enrollment_year, course, building_block,
                semester, cgpa, attendance_percentage, fees_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, data['first_name'], data['last_name'],
            data.get('date_of_birth'), data.get('email'), data.get('phone'),
            data.get('address'), data['department'], data.get('enrollment_year', datetime.now().year),
            data['course'], data['building_block'], data['semester'],
            data['cgpa'], data['attendance_percentage'], data['fees_status']
        ))

        # Initialize subjects and assignments
        subjects = ['Maths', 'Programming', 'Data Structures', 'Database', 'AI']
        for subject in subjects:
            cursor.execute('INSERT INTO subjects (student_id, subject_name, marks) VALUES (?, ?, ?)',
                          (student_id, subject, 0))
            cursor.execute('INSERT INTO assignments (student_id, subject_name, status) VALUES (?, ?, ?)',
                          (student_id, subject, 'Pending'))

        conn.commit()
        conn.close()
        return student_id

    @staticmethod
    def update(student_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE students SET
                first_name = ?, last_name = ?, date_of_birth = ?, email = ?,
                phone = ?, address = ?, department = ?, enrollment_year = ?,
                course = ?, building_block = ?, semester = ?, cgpa = ?,
                attendance_percentage = ?, fees_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?
        ''', (
            data['first_name'], data['last_name'], data.get('date_of_birth'),
            data.get('email'), data.get('phone'), data.get('address'),
            data['department'], data.get('enrollment_year'), data['course'],
            data['building_block'], data['semester'], data['cgpa'],
            data['attendance_percentage'], data['fees_status'], student_id
        ))

        if 'subjects' in data:
            for subject, marks in data['subjects'].items():
                cursor.execute('UPDATE subjects SET marks = ? WHERE student_id = ? AND subject_name = ?',
                              (marks, student_id, subject))

        if 'assignments' in data:
            for subject, status in data['assignments'].items():
                cursor.execute('UPDATE assignments SET status = ? WHERE student_id = ? AND subject_name = ?',
                              (status, student_id, subject))

        conn.commit()
        conn.close()

    @staticmethod
    def delete(student_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assignments WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM subjects WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()

class Subject:
    @staticmethod
    def get_by_student(student_id):
        conn = get_db_connection()
        cursor = conn.execute("SELECT subject_name, marks FROM subjects WHERE student_id = ?", (student_id,))
        subjects = {row['subject_name']: row['marks'] for row in cursor.fetchall()}
        conn.close()
        return subjects

class Assignment:
    @staticmethod
    def get_by_student(student_id):
        conn = get_db_connection()
        cursor = conn.execute("SELECT subject_name, status FROM assignments WHERE student_id = ?", (student_id,))
        assignments = {row['subject_name']: row['status'] for row in cursor.fetchall()}
        conn.close()
        return assignments

class User:
    @staticmethod
    def create(full_name, email, username, password_hash):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (full_name, email, username, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, username, password_hash))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None