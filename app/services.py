# app/services.py
from .database import get_db_connection

class AnalyticsService:
    @staticmethod
    def get_dashboard_stats():
        conn = get_db_connection()

        # Total students
        cursor = conn.execute("SELECT COUNT(*) as count FROM students")
        total_students = cursor.fetchone()['count']

        # Average CGPA
        cursor = conn.execute("SELECT AVG(cgpa) as avg_cgpa FROM students")
        avg_cgpa = round(cursor.fetchone()['avg_cgpa'] or 0, 2)

        # Fees paid (not pending)
        cursor = conn.execute("SELECT COUNT(*) as count FROM students WHERE fees_status = 'Paid'")
        fees_paid = cursor.fetchone()['count']

        # Average attendance
        cursor = conn.execute("SELECT AVG(attendance_percentage) as avg_att FROM students")
        avg_attendance = round(cursor.fetchone()['avg_att'] or 0, 1)

        conn.close()

        return {
            'total_students': total_students,
            'avg_cgpa': avg_cgpa,
            'fees_paid': fees_paid,
            'avg_attendance': avg_attendance
        }

    @staticmethod
    def get_cgpa_distribution():
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT
                CASE
                    WHEN cgpa >= 0 AND cgpa < 2.0 THEN '0-2.0'
                    WHEN cgpa >= 2.0 AND cgpa < 2.5 THEN '2.0-2.5'
                    WHEN cgpa >= 2.5 AND cgpa < 3.0 THEN '2.5-3.0'
                    WHEN cgpa >= 3.0 AND cgpa < 3.5 THEN '3.0-3.5'
                    WHEN cgpa >= 3.5 AND cgpa <= 4.0 THEN '3.5-4.0'
                    ELSE 'Invalid'
                END AS range,
                COUNT(*) as count
            FROM students
            WHERE cgpa IS NOT NULL
            GROUP BY range
            ORDER BY
                CASE
                    WHEN range = '0-2.0' THEN 1
                    WHEN range = '2.0-2.5' THEN 2
                    WHEN range = '2.5-3.0' THEN 3
                    WHEN range = '3.0-3.5' THEN 4
                    WHEN range = '3.5-4.0' THEN 5
                    ELSE 6
                END
        """)

        ranges = []
        counts = []
        for row in cursor.fetchall():
            ranges.append(row['range'])
            counts.append(row['count'])

        conn.close()
        return {
            'labels': ranges,
            'values': counts
        }

    @staticmethod
    def get_department_stats():
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT
                department,
                COUNT(*) as count,
                ROUND(AVG(cgpa), 2) as avg_cgpa,
                ROUND(AVG(attendance_percentage), 1) as avg_attendance
            FROM students
            GROUP BY department
            ORDER BY department
        """)

        departments = []
        counts = []
        for row in cursor.fetchall():
            departments.append(row['department'])
            counts.append(row['count'])

        conn.close()
        return {
            'labels': departments,
            'values': counts
        }

    @staticmethod
    def get_subject_averages():
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT subject_name, ROUND(AVG(marks), 2) as avg_marks
            FROM subjects
            GROUP BY subject_name
            ORDER BY subject_name
        """)

        averages = {row['subject_name']: row['avg_marks'] or 0 for row in cursor.fetchall()}
        conn.close()
        return averages

    @staticmethod
    def get_attendance_distribution():
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT
                CASE
                    WHEN attendance_percentage >= 0 AND attendance_percentage < 60 THEN '0-60%'
                    WHEN attendance_percentage >= 60 AND attendance_percentage < 70 THEN '60-70%'
                    WHEN attendance_percentage >= 70 AND attendance_percentage < 80 THEN '70-80%'
                    WHEN attendance_percentage >= 80 AND attendance_percentage < 90 THEN '80-90%'
                    WHEN attendance_percentage >= 90 AND attendance_percentage <= 100 THEN '90-100%'
                    ELSE 'Invalid'
                END AS range,
                COUNT(*) as count
            FROM students
            WHERE attendance_percentage IS NOT NULL
            GROUP BY range
            ORDER BY
                CASE
                    WHEN range = '0-60%' THEN 1
                    WHEN range = '60-70%' THEN 2
                    WHEN range = '70-80%' THEN 3
                    WHEN range = '80-90%' THEN 4
                    WHEN range = '90-100%' THEN 5
                    ELSE 6
                END
        """)

        distribution = {row['range']: row['count'] for row in cursor.fetchall()}
        conn.close()
        return distribution

    @staticmethod
    def get_assignment_status():
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT subject_name, status, COUNT(*) as count
            FROM assignments
            GROUP BY subject_name, status
            ORDER BY subject_name, status
        """)

        status_data = {}
        for row in cursor.fetchall():
            subject = row['subject_name']
            if subject not in status_data:
                status_data[subject] = {}
            status_data[subject][row['status']] = row['count']

        conn.close()
        return status_data

class StudentService:
    @staticmethod
    def get_pending_fees():
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT student_id, first_name, last_name, department, semester, fees_status
            FROM students
            WHERE fees_status IN ('Pending', 'Partial')
            ORDER BY fees_status, last_name
        """)

        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students

    @staticmethod
    def get_top_students(limit=10):
        conn = get_db_connection()
        cursor = conn.execute("""
            SELECT student_id, first_name, last_name, department, cgpa
            FROM students
            ORDER BY cgpa DESC
            LIMIT ?
        """, (limit,))

        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students

    @staticmethod
    def get_departments():
        conn = get_db_connection()
        cursor = conn.execute("SELECT DISTINCT department FROM students ORDER BY department")
        departments = [row['department'] for row in cursor.fetchall()]
        conn.close()
        return departments