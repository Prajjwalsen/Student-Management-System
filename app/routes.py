# app/routes.py
from flask import render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Student, Subject, Assignment, User
from .services import AnalyticsService, StudentService

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app):
    # Page routes

    @app.route('/')
    def index():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/students')
    @login_required
    def students():
        return render_template('students.html')

    @app.route('/add_student', methods=['GET', 'POST'])
    @login_required
    def add_student():
        success_message = None
        if request.method == 'POST':
            # Here you would add the student to the database
            success_message = 'Student Added Successfully!'
        return render_template('add_student.html', success_message=success_message)

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')

    @app.route('/analytics')
    @login_required
    def analytics():
        return render_template('analytics.html')

    @app.route('/fees')
    @login_required
    def fees():
        return render_template('fees.html')

    @app.route('/assignments')
    @login_required
    def assignments():
        return render_template('assignments.html')

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.get_by_username(username)
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            full_name = request.form['full_name']
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('register.html')
            
            if User.get_by_username(username):
                flash('Username already exists', 'error')
                return render_template('register.html')
            
            if User.get_by_email(email):
                flash('Email already exists', 'error')
                return render_template('register.html')
            
            password_hash = generate_password_hash(password)
            User.create(full_name, email, username, password_hash)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    # API routes
    @app.route('/api/students')
    def get_students():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search', '')
        department = request.args.get('department', '')
        semester = request.args.get('semester', '')

        students, total = Student.get_all(page, per_page, search, department, semester)

        return jsonify({
            'students': students,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })

    @app.route('/api/student/<student_id>')
    def get_student(student_id):
        student = Student.get_by_id(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        # Add subjects and assignments
        student.update(Subject.get_by_student(student_id))
        assignments = Assignment.get_by_student(student_id)
        for key, value in assignments.items():
            student[f"{key.lower()}_assignment_status"] = value

        return jsonify(student)

    @app.route('/api/student', methods=['POST'])
    def create_student():
        data = request.get_json()

        try:
            student_id = Student.create(data)
            return jsonify({'success': True, 'student_id': student_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/student/<student_id>', methods=['PUT'])
    def update_student(student_id):
        data = request.get_json()

        try:
            Student.update(student_id, data)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/student/<student_id>', methods=['DELETE'])
    def delete_student(student_id):
        try:
            Student.delete(student_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/departments')
    def get_departments():
        return jsonify(StudentService.get_departments())

    @app.route('/api/dashboard-stats')
    def get_dashboard_stats():
        return jsonify(AnalyticsService.get_dashboard_stats())

    @app.route('/api/department-stats')
    def get_department_stats():
        return jsonify(AnalyticsService.get_department_stats())

    @app.route('/api/cgpa-distribution')
    def get_cgpa_distribution():
        return jsonify(AnalyticsService.get_cgpa_distribution())

    @app.route('/api/students/pending-fees')
    def get_pending_fees():
        return jsonify(StudentService.get_pending_fees())

    @app.route('/api/students/top-cgpa')
    def get_top_students():
        limit = int(request.args.get('limit', 10))
        return jsonify(StudentService.get_top_students(limit))

    @app.route('/api/analytics/subject-averages')
    def get_subject_averages():
        return jsonify(AnalyticsService.get_subject_averages())

    @app.route('/api/analytics/attendance-distribution')
    def get_attendance_distribution():
        return jsonify(AnalyticsService.get_attendance_distribution())

    @app.route('/api/assignments/status')
    def get_assignment_status():
        return jsonify(AnalyticsService.get_assignment_status())

    @app.route('/api/assignments')
    def get_assignments():
        subject = request.args.get('subject', '')
        status = request.args.get('status', '')
        # For now, return empty data - this would be implemented with actual assignment data
        return jsonify([])

    @app.route('/api/assignment/<assignment_id>', methods=['PUT', 'DELETE'])
    def handle_assignment(assignment_id):
        if request.method == 'PUT':
            # Update assignment logic here
            return jsonify({'success': True})
        elif request.method == 'DELETE':
            # Delete assignment logic here
            return jsonify({'success': True})

    @app.route('/api/assignment', methods=['POST'])
    def create_assignment():
        # Create assignment logic here
        return jsonify({'success': True})