// Student Management System - Main JavaScript File

// Global variables
let currentEditStudentId = null;
let currentDeleteStudentId = null;

// Utility functions
function showLoading(element) {
    if (element) {
        element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    }
}

function hideLoading(element, originalContent) {
    if (element && originalContent) {
        element.innerHTML = originalContent;
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
}

// Success and error functions for compatibility
function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

// Export functionality
async function exportReport(type = 'students') {
    try {
        showNotification('Generating report...', 'info');
        
        let data, filename;
        
        switch(type) {
            case 'students':
                data = await exportStudentsReport();
                filename = 'students_report.csv';
                break;
            case 'analytics':
                data = await exportAnalyticsReport();
                filename = 'analytics_report.csv';
                break;
            default:
                data = await exportStudentsReport();
                filename = 'report.csv';
        }
        
        downloadCSV(data, filename);
        showNotification('Report exported successfully!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showError('Failed to export report');
    }
}

async function exportStudentsReport() {
    const response = await fetch('/api/students?per_page=1000');
    const data = await response.json();
    
    let csv = 'Student ID,First Name,Last Name,Email,Phone,Department,Semester,CGPA,Attendance,Fees Status\n';
    
    if (data.students && data.students.length > 0) {
        data.students.forEach(student => {
            csv += `${student.student_id},"${student.first_name}","${student.last_name}","${student.email || ''}","${student.phone || ''}","${student.department}",${student.semester},"${student.cgpa || 'N/A'}",${student.attendance_percentage}%,"${student.fees_status}"\n`;
        });
    } else {
        csv += 'No data found\n';
    }
    
    return csv;
}

async function exportAnalyticsReport() {
    try {
        const [statsResponse, deptResponse, cgpaResponse] = await Promise.all([
            fetch('/api/dashboard-stats'),
            fetch('/api/department-stats'),
            fetch('/api/cgpa-distribution')
        ]);
        
        const stats = await statsResponse.json();
        const deptData = await deptResponse.json();
        const cgpaData = await cgpaResponse.json();
        
        let csv = 'Analytics Report\n\n';
        csv += 'Dashboard Statistics\n';
        csv += `Total Students,${stats.total_students || 0}\n`;
        csv += `Average CGPA,${stats.avg_cgpa || 0}\n`;
        csv += `Fees Paid,${stats.fees_paid || 0}\n`;
        csv += `Average Attendance,${stats.avg_attendance || 0}%\n\n`;
        
        csv += 'Department Distribution\n';
        csv += 'Department,Count\n';
        if (deptData.labels && deptData.values) {
            deptData.labels.forEach((dept, index) => {
                csv += `"${dept}",${deptData.values[index] || 0}\n`;
            });
        } else {
            csv += 'No data available\n';
        }
        
        csv += '\nCGPA Distribution\n';
        csv += 'Range,Count\n';
        if (cgpaData.labels && cgpaData.values) {
            cgpaData.labels.forEach((range, index) => {
                csv += `"${range}",${cgpaData.values[index] || 0}\n`;
            });
        } else {
            csv += 'No data available\n';
        }
        
        return csv;
    } catch (error) {
        console.error('Error generating analytics report:', error);
        return 'Error generating analytics report\n';
    }
}

function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// API call helper
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
});

// Student management functions
async function loadStudents(page = 1, search = '', department = '', semester = '') {
    try {
        showLoading(document.querySelector('#students-table tbody'));
        
        const params = new URLSearchParams({
            page: page,
            per_page: 20,
            search: search,
            department: department,
            semester: semester
        });
        
        const data = await apiCall(`/api/students?${params}`);
        renderStudentsTable(data.students);
        updatePagination(data);
        
    } catch (error) {
        console.error('Error loading students:', error);
        showNotification('Error loading students', 'error');
    }
}

function renderStudentsTable(students) {
    const tbody = document.querySelector('#students-table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    students.forEach(student => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${student.student_id}</td>
            <td>${student.first_name} ${student.last_name}</td>
            <td>${student.department}</td>
            <td>${student.semester}</td>
            <td>${student.cgpa}</td>
            <td><span class="status-badge ${student.fees_status.toLowerCase()}">${student.fees_status}</span></td>
            <td>
                <button class="btn-primary btn-sm" onclick="viewProfile('${student.student_id}')" title="View Profile">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn-secondary btn-sm" onclick="editStudent('${student.student_id}')" title="Edit Student">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-danger btn-sm" onclick="deleteStudent('${student.student_id}', '${student.first_name} ${student.last_name}')" title="Delete Student">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
    });
}

function updatePagination(data) {
    // Update pagination controls if they exist
    const pagination = document.querySelector('.pagination');
    if (pagination) {
        // Implementation depends on your pagination UI
    }
}

async function viewProfile(studentId) {
    window.location.href = `/profile?id=${studentId}`;
}

async function editStudent(studentId) {
    try {
        const student = await apiCall(`/api/student/${studentId}`);
        currentEditStudentId = studentId;
        
        // Populate edit form
        document.getElementById('edit-student-id').value = student.student_id;
        document.getElementById('edit-first-name').value = student.first_name;
        document.getElementById('edit-last-name').value = student.last_name;
        document.getElementById('edit-department').value = student.department;
        document.getElementById('edit-semester').value = student.semester;
        document.getElementById('edit-cgpa').value = student.cgpa;
        document.getElementById('edit-attendance').value = student.attendance_percentage;
        document.getElementById('edit-fees-status').value = student.fees_status;
        
        openModal('edit-student-modal');
    } catch (error) {
        console.error('Error loading student for edit:', error);
        showNotification('Error loading student data', 'error');
    }
}

async function saveStudent() {
    if (!validateForm('edit-student-form')) {
        showNotification('Please fill all required fields', 'error');
        return;
    }
    
    try {
        const formData = {
            first_name: document.getElementById('edit-first-name').value,
            last_name: document.getElementById('edit-last-name').value,
            department: document.getElementById('edit-department').value,
            semester: document.getElementById('edit-semester').value,
            cgpa: parseFloat(document.getElementById('edit-cgpa').value),
            attendance_percentage: parseFloat(document.getElementById('edit-attendance').value),
            fees_status: document.getElementById('edit-fees-status').value
        };
        
        await apiCall(`/api/student/${currentEditStudentId}`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });
        
        closeModal('edit-student-modal');
        loadStudents();
        showNotification('Student updated successfully', 'success');
        
    } catch (error) {
        console.error('Error saving student:', error);
        showNotification('Error saving student', 'error');
    }
}

function deleteStudent(studentId, studentName) {
    currentDeleteStudentId = studentId;
    document.getElementById('delete-student-name').textContent = studentName;
    openModal('delete-student-modal');
}

async function confirmDelete() {
    try {
        await apiCall(`/api/student/${currentDeleteStudentId}`, {
            method: 'DELETE'
        });
        
        closeModal('delete-student-modal');
        loadStudents();
        showNotification('Student deleted successfully', 'success');
        
    } catch (error) {
        console.error('Error deleting student:', error);
        showNotification('Error deleting student', 'error');
    }
}

// Add student functions
async function addStudent() {
    if (!validateForm('add-student-form')) {
        showNotification('Please fill all required fields', 'error');
        return;
    }
    
    try {
        const formData = {
            student_id: document.getElementById('student-id').value,
            first_name: document.getElementById('first-name').value,
            last_name: document.getElementById('last-name').value,
            department: document.getElementById('department').value,
            semester: document.getElementById('semester').value,
            cgpa: parseFloat(document.getElementById('cgpa').value),
            attendance_percentage: parseFloat(document.getElementById('attendance').value),
            fees_status: document.getElementById('fees-status').value
        };
        
        await apiCall('/api/student', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        document.getElementById('add-student-form').reset();
        showNotification('Student added successfully', 'success');
        
        // Redirect to students page after a short delay
        setTimeout(() => {
            window.location.href = '/students';
        }, 1500);
        
    } catch (error) {
        console.error('Error adding student:', error);
        showNotification('Error adding student', 'error');
    }
}

// Load departments for dropdowns
async function loadDepartments() {
    try {
        const departments = await apiCall('/api/departments');
        const selects = document.querySelectorAll('select[id="department"], select[id="edit-department"], select[id="assignment-department-filter"]');
        
        selects.forEach(select => {
            // Clear existing options except the first one
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept;
                option.textContent = dept;
                select.appendChild(option);
            });
        });
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

// Profile page functions
async function loadStudentProfile() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const studentId = urlParams.get('id');
        
        if (!studentId) {
            showNotification('No student ID provided', 'error');
            return;
        }
        
        const student = await apiCall(`/api/student/${studentId}`);
        renderProfileData(student);
        
    } catch (error) {
        console.error('Error loading student profile:', error);
        showNotification('Error loading student profile', 'error');
    }
}

function renderProfileData(student) {
    // Hide loading and show data
    const loadingElement = document.getElementById('profile-loading');
    const dataElement = document.getElementById('profile-data');
    
    if (loadingElement) loadingElement.style.display = 'none';
    if (dataElement) dataElement.style.display = 'block';
    
    // Fill profile data
    const elements = {
        'student-name': `${student.first_name} ${student.last_name}`,
        'student-id': student.student_id,
        'student-department': student.department,
        'dob': student.date_of_birth || 'N/A',
        'email': student.email || 'N/A',
        'phone': student.phone || 'N/A',
        'address': student.address || 'N/A',
        'department': student.department,
        'course': student.course || 'N/A',
        'semester': student.semester,
        'building': student.building_block || 'N/A',
        'enrollment': student.enrollment_year || 'N/A',
        'cgpa': student.cgpa,
        'attendance': (student.attendance_percentage || 0) + '%'
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
    
    // Fees status with badge
    const feesStatusElement = document.getElementById('fees-status');
    if (feesStatusElement) {
        feesStatusElement.innerHTML = `<span class="status-badge ${student.fees_status?.toLowerCase() || 'pending'}">${student.fees_status || 'Pending'}</span>`;
    }
    
    // Subject marks
    const marks = {
        'maths-marks': student.Maths || 0,
        'programming-marks': student.Programming || 0,
        'ds-marks': student['Data Structures'] || 0,
        'db-marks': student.Database || 0,
        'ai-marks': student.AI || 0
    };
    
    Object.keys(marks).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = marks[id];
        }
    });
    
    // Assignment status
    const assignments = {
        'maths-assignment': student.maths_assignment_status || 'Pending',
        'programming-assignment': student.programming_assignment_status || 'Pending',
        'ds-assignment': student.data_structures_assignment_status || 'Pending',
        'db-assignment': student.database_assignment_status || 'Pending',
        'ai-assignment': student.ai_assignment_status || 'Pending'
    };
    
    Object.keys(assignments).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            const status = assignments[id];
            element.innerHTML = `<span class="status-badge ${status.toLowerCase()}">${status}</span>`;
        }
    });
}

// Analytics functions
async function loadAnalyticsData() {
    try {
        // Load all analytics data
        const [cgpaDist, deptStats, subjectAvg, attendanceDist] = await Promise.all([
            apiCall('/api/cgpa-distribution'),
            apiCall('/api/department-stats'),
            apiCall('/api/analytics/subject-averages'),
            apiCall('/api/analytics/attendance-distribution')
        ]);
        
        renderAnalyticsCharts(cgpaDist, deptStats, subjectAvg, attendanceDist);
        
    } catch (error) {
        console.error('Error loading analytics data:', error);
        showNotification('Error loading analytics data', 'error');
    }
}

function renderAnalyticsCharts(cgpaDist, deptStats, subjectAvg, attendanceDist) {
    // Implementation depends on your analytics page structure
    // This would create Chart.js charts for the analytics page
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load departments if we have dropdowns
    if (document.querySelector('select[id="department"]')) {
        loadDepartments();
    }
    
    // Load profile data if we're on the profile page
    if (document.getElementById('profile-loading')) {
        loadStudentProfile();
    }
    
    // Load analytics data if we're on the analytics page
    if (document.getElementById('analytics-charts')) {
        loadAnalyticsData();
    }
});

// Export functions for global access
window.SMS = {
    showNotification,
    openModal,
    closeModal,
    loadStudents,
    editStudent,
    saveStudent,
    deleteStudent,
    confirmDelete,
    addStudent,
    viewProfile,
    loadDepartments
};
