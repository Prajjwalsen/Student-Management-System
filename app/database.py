# app/database.py
import sqlite3
import pandas as pd
import os

DATABASE = 'database.db'

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with tables and load CSV data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            email TEXT,
            phone TEXT,
            address TEXT,
            department TEXT,
            enrollment_year INTEGER,
            course TEXT,
            building_block TEXT,
            semester INTEGER,
            cgpa REAL,
            attendance_percentage REAL,
            fees_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject_name TEXT,
            marks INTEGER,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')

    # Create assignments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject_name TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Check if default admin user exists
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
    admin_count = cursor.fetchone()['count']
    
    if admin_count == 0:
        # Create default admin user
        from werkzeug.security import generate_password_hash
        admin_password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (full_name, email, username, password_hash)
            VALUES (?, ?, ?, ?)
        ''', ('Administrator', 'admin@example.com', 'admin', admin_password_hash))
        print("Created default admin user (username: admin, password: admin123)")

    conn.commit()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) as count FROM students")
    student_count = cursor.fetchone()['count']

    if student_count == 0:
        # Load CSV data
        try:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'Student_Management_System_Expanded.csv')
            df = pd.read_csv(csv_path)

            print(f"Loading {len(df)} records from CSV to database...")

            for _, row in df.iterrows():
                # Insert student
                cursor.execute('''
                    INSERT INTO students (
                        student_id, first_name, last_name, date_of_birth, email, phone,
                        address, department, enrollment_year, course, building_block,
                        semester, cgpa, attendance_percentage, fees_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['StudentID'], row['FirstName'], row['LastName'],
                    row['DateOfBirth'], row['Email'], row['Phone'], row['Address'],
                    row['Department'], row['EnrollmentYear'], row['Course'],
                    row['Building_Block'], row['Semester'], row['CGPA'],
                    row['Attendance_Percentage'], row['Fees_Status']
                ))

                # Insert subject marks
                subjects = [
                    ('Maths', row['Maths_Marks']),
                    ('Programming', row['Programming_Marks']),
                    ('Data Structures', row['Data Structures_Marks']),
                    ('Database', row['Database_Marks']),
                    ('AI', row['AI_Marks'])
                ]

                for subject_name, marks in subjects:
                    cursor.execute('''
                        INSERT INTO subjects (student_id, subject_name, marks)
                        VALUES (?, ?, ?)
                    ''', (row['StudentID'], subject_name, marks))

                # Insert assignment status
                assignments = [
                    ('Maths', row['Maths_Assignment_Status']),
                    ('Programming', row['Programming_Assignment_Status']),
                    ('Data Structures', row['Data Structures_Assignment_Status']),
                    ('Database', row['Database_Assignment_Status']),
                    ('AI', row['AI_Assignment_Status'])
                ]

                for subject_name, status in assignments:
                    cursor.execute('''
                        INSERT INTO assignments (student_id, subject_name, status)
                        VALUES (?, ?, ?)
                    ''', (row['StudentID'], subject_name, status))

            conn.commit()
            print(f"Successfully loaded {len(df)} student records to database!")

        except Exception as e:
            print(f"Error loading CSV data: {e}")
            conn.rollback()

    conn.close()