---
title: "Instructor and TA Documentation"
sidebar_label: "Instructor & TA Guide"
sidebar_position: 114
---

# Instructor and TA Documentation for Physical AI & Humanoid Robotics Course

## Overview

This comprehensive guide provides instructors and teaching assistants with all necessary information to effectively deliver the Physical AI & Humanoid Robotics course. It includes course administration, technical setup, grading guidelines, troubleshooting, and best practices for student support.

## Course Administration

### 1. Course Setup and Configuration

#### Initial Course Setup
```bash
# Course setup checklist for instructors
# 1. Environment Setup
# Install required software and dependencies
sudo apt update
sudo apt install ros-humble-desktop-full
sudo apt install gazebo11 gz-tools1 python3-rosdep python3-colcon-common-extensions

# 2. Course Repository Setup
git clone https://github.com/institution/robotics-course.git
cd robotics-course

# 3. Create instructor environment
cp .env.example .env
# Edit .env with institutional settings
INSTITUTION_NAME="Your Institution Name"
COURSE_CODE="CS475"
SEMESTER="Fall 2025"
INSTRUCTOR_EMAIL="instructor@your-institution.edu"
TA_EMAILS="ta1@your-institution.edu,ta2@your-institution.edu"

# 4. Initialize course environment
./scripts/setup-instructor-environment.sh
```

#### Course Management Dashboard
```python
# instructor_dashboard.py
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
from typing import Dict, List, Any

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class InstructorDashboard:
    def __init__(self):
        self.course_stats = {
            'total_students': 0,
            'active_students': 0,
            'module_completion': {},
            'assignment_submissions': {},
            'technical_issues': {},
            'feedback_summary': {}
        }

    def get_course_overview(self) -> Dict[str, Any]:
        """Get comprehensive course overview for instructors"""
        return {
            'course_info': {
                'course_code': 'CS475',
                'course_name': 'Physical AI & Humanoid Robotics',
                'semester': 'Fall 2025',
                'instructor': 'Dr. Jane Smith',
                'total_students': 150,
                'start_date': '2025-09-01',
                'end_date': '2025-12-15'
            },
            'progress_metrics': {
                'overall_completion_rate': 0.68,
                'average_grade': 78.5,
                'attendance_rate': 0.85,
                'assignment_submission_rate': 0.92
            },
            'module_progress': {
                'module_1': {'name': 'ROS 2 Fundamentals', 'completion_rate': 0.92, 'avg_grade': 82.3},
                'module_2': {'name': 'Simulation Environments', 'completion_rate': 0.85, 'avg_grade': 79.1},
                'module_3': {'name': 'AI Integration with Isaac', 'completion_rate': 0.78, 'avg_grade': 75.4},
                'module_4': {'name': 'Voice-Controlled Robotics', 'completion_rate': 0.65, 'avg_grade': 72.8}
            },
            'at_risk_students': ['student_001', 'student_002', 'student_003'],
            'recent_activities': self._get_recent_activities(),
            'last_updated': datetime.utcnow().isoformat()
        }

    def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent course activities"""
        return [
            {'timestamp': '2025-10-15T10:30:00Z', 'activity': 'Assignment 3 grades released', 'actor': 'instructor'},
            {'timestamp': '2025-10-14T15:45:00Z', 'activity': 'Module 2 content updated', 'actor': 'instructor'},
            {'timestamp': '2025-10-14T09:15:00Z', 'activity': 'Technical issue reported by 5 students', 'actor': 'system'},
            {'timestamp': '2025-10-13T16:20:00Z', 'activity': 'Office hours attendance: 12 students', 'actor': 'ta'}
        ]

    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get detailed progress for a specific student"""
        return {
            'student_id': student_id,
            'name': 'John Doe',
            'email': 'jdoe@institution.edu',
            'overall_progress': 75.5,
            'module_progress': {
                'module_1': 95.0,
                'module_2': 80.0,
                'module_3': 65.0,
                'module_4': 42.0
            },
            'assignment_scores': [
                {'assignment': 'ROS Basics', 'score': 92, 'max_score': 100},
                {'assignment': 'Simulation Setup', 'score': 85, 'max_score': 100},
                {'assignment': 'Isaac Integration', 'score': 70, 'max_score': 100},
                {'assignment': 'Voice Control', 'score': 45, 'max_score': 100}
            ],
            'participation': {
                'forum_posts': 23,
                'peer_reviews_completed': 8,
                'attendance_rate': 0.88
            },
            'support_needed': ['Module 3 debugging', 'Module 4 conceptual help'],
            'last_access': '2025-10-15T14:30:00Z'
        }

    def get_class_analytics(self) -> Dict[str, Any]:
        """Get comprehensive class analytics"""
        return {
            'enrollment': {
                'total_enrolled': 150,
                'active_participants': 142,
                'drop_rate': 0.05
            },
            'performance': {
                'class_average': 78.5,
                'grade_distribution': {
                    'A': 25,  # 16.7%
                    'B': 45,  # 30.0%
                    'C': 52,  # 34.7%
                    'D': 18,  # 12.0%
                    'F': 10   # 6.7%
                },
                'standard_deviation': 12.3
            },
            'engagement': {
                'average_time_on_platform': 4.2,  # hours per week
                'assignment_completion_rate': 0.89,
                'forum_participation_rate': 0.76
            },
            'trends': {
                'weekly_progress': [65.2, 68.1, 71.5, 73.2, 75.8],  # Last 5 weeks
                'engagement_trend': 'increasing',
                'performance_trend': 'stable'
            }
        }

instructor_dashboard = InstructorDashboard()

@app.route('/instructor/dashboard')
def instructor_dashboard_view():
    """Main instructor dashboard view"""
    course_overview = instructor_dashboard.get_course_overview()
    return render_template('instructor_dashboard.html', overview=course_overview)

@app.route('/api/instructor/course/overview')
def api_course_overview():
    """API endpoint for course overview data"""
    return jsonify(instructor_dashboard.get_course_overview())

@app.route('/api/instructor/student/<student_id>/progress')
def api_student_progress(student_id):
    """API endpoint for student progress"""
    progress = instructor_dashboard.get_student_progress(student_id)
    return jsonify(progress)

@app.route('/api/instructor/class/analytics')
def api_class_analytics():
    """API endpoint for class analytics"""
    analytics = instructor_dashboard.get_class_analytics()
    return jsonify(analytics)
```

### 2. Student Management

#### Student Enrollment and Access
```python
# student_management.py
import csv
import hashlib
from typing import Dict, List, Any
from datetime import datetime

class StudentManager:
    def __init__(self):
        self.students = {}
        self.enrollment_codes = {}

    def bulk_enroll_students(self, csv_file_path: str) -> Dict[str, Any]:
        """Enroll students from CSV file"""
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        try:
            with open(csv_file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    student_data = {
                        'student_id': row.get('student_id'),
                        'first_name': row.get('first_name'),
                        'last_name': row.get('last_name'),
                        'email': row.get('email'),
                        'section': row.get('section', 'A'),
                        'enrollment_date': datetime.utcnow().isoformat()
                    }

                    success = self.enroll_student(student_data)
                    if success:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to enroll: {student_data.get('email')}")

        except Exception as e:
            results['errors'].append(f"CSV processing error: {str(e)}")

        return results

    def enroll_student(self, student_data: Dict[str, Any]) -> bool:
        """Enroll a single student"""
        try:
            # Validate required fields
            required_fields = ['student_id', 'first_name', 'last_name', 'email']
            for field in required_fields:
                if not student_data.get(field):
                    return False

            # Generate unique access credentials
            student_id = student_data['student_id']
            access_token = self._generate_access_token(student_id)
            password_hash = self._generate_password_hash(student_data['email'])

            # Store student data
            self.students[student_id] = {
                **student_data,
                'access_token': access_token,
                'password_hash': password_hash,
                'status': 'active',
                'progress': {},
                'grades': {},
                'preferences': {
                    'communication': 'email',
                    'timezone': 'UTC',
                    'notification_frequency': 'daily'
                }
            }

            return True

        except Exception as e:
            print(f"Enrollment error: {e}")
            return False

    def _generate_access_token(self, student_id: str) -> str:
        """Generate secure access token for student"""
        import secrets
        return secrets.token_urlsafe(32)

    def _generate_password_hash(self, email: str) -> str:
        """Generate password hash using email as base"""
        import secrets
        salt = secrets.token_hex(16)
        password = f"{email}_{secrets.token_hex(8)}"
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{password_hash.hex()}"

    def get_student_list(self, section: str = None) -> List[Dict[str, Any]]:
        """Get list of students, optionally filtered by section"""
        students = list(self.students.values())

        if section:
            students = [s for s in students if s.get('section') == section]

        return students

    def update_student_status(self, student_id: str, status: str) -> bool:
        """Update student enrollment status"""
        if student_id in self.students:
            self.students[student_id]['status'] = status
            return True
        return False

    def generate_student_report(self, student_id: str) -> Dict[str, Any]:
        """Generate comprehensive student report for instructors"""
        if student_id not in self.students:
            return None

        student = self.students[student_id]

        return {
            'student_info': {
                'student_id': student['student_id'],
                'name': f"{student['first_name']} {student['last_name']}",
                'email': student['email'],
                'section': student.get('section', 'N/A')
            },
            'course_progress': student.get('progress', {}),
            'grades': student.get('grades', {}),
            'activity_metrics': self._calculate_activity_metrics(student_id),
            'support_recommendations': self._generate_support_recommendations(student_id),
            'generated_at': datetime.utcnow().isoformat()
        }

    def _calculate_activity_metrics(self, student_id: str) -> Dict[str, Any]:
        """Calculate activity metrics for a student"""
        # Implementation would calculate metrics from database
        # This is a simplified example
        return {
            'days_active': 45,
            'pages_viewed': 234,
            'assignments_completed': 12,
            'forum_posts': 18,
            'peer_reviews_completed': 8,
            'average_session_time': 35  # minutes
        }

    def _generate_support_recommendations(self, student_id: str) -> List[str]:
        """Generate support recommendations for a student"""
        recommendations = []

        # Example logic - in real implementation, this would use actual data
        if student_id in ['student_001', 'student_002']:  # Example at-risk students
            recommendations.extend([
                'Schedule one-on-one meeting to discuss progress',
                'Recommend additional tutoring resources',
                'Suggest forming study group with high-performing peers'
            ])

        return recommendations

student_manager = StudentManager()
```

### 3. Grade Management

#### Grading System and Rubrics
```python
# grading_system.py
from typing import Dict, List, Any
from datetime import datetime
import statistics

class GradingSystem:
    def __init__(self):
        self.assignment_types = {
            'exercise': {'weight': 0.20, 'max_points': 100},
            'quiz': {'weight': 0.15, 'max_points': 100},
            'project': {'weight': 0.30, 'max_points': 100},
            'participation': {'weight': 0.10, 'max_points': 100},
            'peer_review': {'weight': 0.10, 'max_points': 100},
            'final_exam': {'weight': 0.15, 'max_points': 100}
        }

        self.grade_scale = {
            'A+': (97, 100),
            'A': (93, 96.9),
            'A-': (90, 92.9),
            'B+': (87, 89.9),
            'B': (83, 86.9),
            'B-': (80, 82.9),
            'C+': (77, 79.9),
            'C': (73, 76.9),
            'C-': (70, 72.9),
            'D': (60, 69.9),
            'F': (0, 59.9)
        }

    def calculate_final_grade(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """Calculate final grade for a student"""
        # Get all assignment scores for the student
        assignments = self._get_student_assignments(student_id, course_id)

        # Group by assignment type
        grouped_scores = {}
        for assignment in assignments:
            assignment_type = assignment['type']
            if assignment_type not in grouped_scores:
                grouped_scores[assignment_type] = []
            grouped_scores[assignment_type].append(assignment['score'])

        # Calculate weighted average
        total_weighted_score = 0
        total_weight = 0

        breakdown = {}
        for assignment_type, scores in grouped_scores.items():
            if assignment_type in self.assignment_types:
                type_weight = self.assignment_types[assignment_type]['weight']
                avg_score = statistics.mean(scores) if scores else 0
                weighted_score = avg_score * type_weight
                total_weighted_score += weighted_score
                total_weight += type_weight

                breakdown[assignment_type] = {
                    'average_score': round(avg_score, 2),
                    'weight': type_weight,
                    'weighted_score': round(weighted_score, 2),
                    'count': len(scores)
                }

        # Calculate final percentage (weighted average)
        final_percentage = (total_weighted_score / total_weight) if total_weight > 0 else 0

        # Determine letter grade
        letter_grade = self._get_letter_grade(final_percentage)

        return {
            'student_id': student_id,
            'final_percentage': round(final_percentage, 2),
            'letter_grade': letter_grade,
            'grade_points': self._letter_to_grade_points(letter_grade),
            'breakdown': breakdown,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def _get_student_assignments(self, student_id: str, course_id: str) -> List[Dict[str, Any]]:
        """Get all assignments for a student in a course"""
        # Implementation would fetch from database
        # This is a simplified example
        return [
            {'type': 'exercise', 'score': 85, 'max_score': 100},
            {'type': 'exercise', 'score': 92, 'max_score': 100},
            {'type': 'quiz', 'score': 78, 'max_score': 100},
            {'type': 'project', 'score': 88, 'max_score': 100},
            {'type': 'participation', 'score': 95, 'max_score': 100},
            {'type': 'peer_review', 'score': 82, 'max_score': 100}
        ]

    def _get_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        for letter, (min_pct, max_pct) in self.grade_scale.items():
            if min_pct <= percentage <= max_pct:
                return letter
        return 'F'  # Default to F if no match

    def _letter_to_grade_points(self, letter_grade: str) -> float:
        """Convert letter grade to grade points"""
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'F': 0.0
        }
        return grade_points.get(letter_grade, 0.0)

    def create_assignment_rubric(self, assignment_id: str, criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed rubric for an assignment"""
        rubric = {
            'assignment_id': assignment_id,
            'criteria': criteria,
            'total_points': sum(c['points'] for c in criteria),
            'created_at': datetime.utcnow().isoformat(),
            'last_modified': datetime.utcnow().isoformat(),
            'status': 'active'
        }

        # Store rubric
        # store_assignment_rubric(rubric)

        return rubric

    def grade_assignment(self, submission_id: str, grader_id: str, scores: Dict[str, float]) -> Dict[str, Any]:
        """Grade an assignment using the rubric"""
        # Get assignment rubric
        rubric = self._get_assignment_rubric(submission_id)

        # Calculate total score
        total_score = 0
        for criterion_id, score in scores.items():
            criterion = next((c for c in rubric['criteria'] if c['id'] == criterion_id), None)
            if criterion:
                # Validate score is within criterion range
                max_points = criterion['points']
                if 0 <= score <= max_points:
                    total_score += score
                else:
                    raise ValueError(f"Score {score} for criterion {criterion_id} is out of range (0-{max_points})")

        # Calculate percentage
        total_possible = sum(c['points'] for c in rubric['criteria'])
        percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0

        # Create grade record
        grade_record = {
            'submission_id': submission_id,
            'grader_id': grader_id,
            'scores': scores,
            'total_score': total_score,
            'total_possible': total_possible,
            'percentage': round(percentage, 2),
            'graded_at': datetime.utcnow().isoformat(),
            'status': 'graded'
        }

        # Store grade
        # store_assignment_grade(grade_record)

        return grade_record

    def get_class_grades(self, course_id: str) -> Dict[str, Any]:
        """Get comprehensive class grade statistics"""
        # Get all student grades for the course
        all_grades = self._get_all_course_grades(course_id)

        if not all_grades:
            return {
                'course_id': course_id,
                'student_count': 0,
                'class_average': 0,
                'grade_distribution': {},
                'standard_deviation': 0
            }

        # Calculate statistics
        percentages = [student['final_percentage'] for student in all_grades]
        class_average = statistics.mean(percentages) if percentages else 0
        std_deviation = statistics.stdev(percentages) if len(percentages) > 1 else 0

        # Calculate grade distribution
        grade_distribution = self._calculate_grade_distribution(percentages)

        return {
            'course_id': course_id,
            'student_count': len(all_grades),
            'class_average': round(class_average, 2),
            'grade_distribution': grade_distribution,
            'standard_deviation': round(std_deviation, 2),
            'highest_grade': max(percentages) if percentages else 0,
            'lowest_grade': min(percentages) if percentages else 0,
            'median_grade': statistics.median(percentages) if percentages else 0
        }

    def _calculate_grade_distribution(self, percentages: List[float]) -> Dict[str, int]:
        """Calculate grade distribution"""
        distribution = {grade: 0 for grade in self.grade_scale.keys()}

        for pct in percentages:
            letter = self._get_letter_grade(pct)
            distribution[letter] += 1

        return distribution

    def _get_all_course_grades(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all grades for a course"""
        # Implementation would fetch from database
        # This is a simplified example
        return [
            {'student_id': 'student_001', 'final_percentage': 85.5},
            {'student_id': 'student_002', 'final_percentage': 92.0},
            {'student_id': 'student_003', 'final_percentage': 78.5}
        ]

grading_system = GradingSystem()
```

## Technical Support and Troubleshooting

### 1. Common Technical Issues

#### ROS 2 Troubleshooting Guide
```python
# ros2_troubleshooting.py
import subprocess
import os
import sys
from typing import Dict, List, Any

class ROS2TroubleshootingGuide:
    def __init__(self):
        self.common_issues = {
            'ros2_daemon_not_running': {
                'symptoms': ['ROS 2 commands not found', 'ros2: command not found'],
                'solutions': [
                    'Source ROS 2 setup: source /opt/ros/humble/setup.bash',
                    'Check ROS 2 installation: dpkg -l | grep ros-humble',
                    'Restart ROS 2 daemon: ros2 daemon stop && ros2 daemon start'
                ],
                'severity': 'high'
            },
            'package_not_found': {
                'symptoms': ['Package not found', 'ament_cmake not found'],
                'solutions': [
                    'Install missing packages: sudo apt install ros-humble-ament-cmake',
                    'Update rosdep: rosdep update',
                    'Install dependencies: rosdep install --from-paths src --ignore-src -r -y'
                ],
                'severity': 'high'
            },
            'build_errors': {
                'symptoms': ['CMake errors', 'Build fails', 'Missing dependencies'],
                'solutions': [
                    'Clean build: rm -rf build install log',
                    'Check dependencies: rosdep install --from-paths src --ignore-src -r -y',
                    'Build specific package: colcon build --packages-select package_name'
                ],
                'severity': 'high'
            },
            'network_discovery': {
                'symptoms': ['Nodes not communicating', 'No topic data'],
                'solutions': [
                    'Check ROS_DOMAIN_ID: echo $ROS_DOMAIN_ID',
                    'Verify network connectivity: ping other_machine',
                    'Check firewall settings: sudo ufw status'
                ],
                'severity': 'medium'
            }
        }

    def diagnose_issue(self, error_message: str) -> Dict[str, Any]:
        """Diagnose ROS 2 issue based on error message"""
        # Find matching issue
        for issue_key, issue_info in self.common_issues.items():
            for symptom in issue_info['symptoms']:
                if symptom.lower() in error_message.lower():
                    return {
                        'issue_key': issue_key,
                        'description': issue_info,
                        'recommended_solutions': issue_info['solutions'],
                        'severity': issue_info['severity']
                    }

        # If no specific issue found, provide general troubleshooting
        return {
            'issue_key': 'unknown',
            'description': {'symptoms': [error_message]},
            'recommended_solutions': [
                'Check ROS 2 installation: source /opt/ros/humble/setup.bash',
                'Verify environment: printenv | grep ROS',
                'Check documentation: https://docs.ros.org/en/humble/',
                'Ask for help in course forums'
            ],
            'severity': 'unknown'
        }

    def run_ros2_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive ROS 2 diagnostics"""
        diagnostics = {
            'environment_check': self._check_environment(),
            'installation_check': self._check_installation(),
            'network_check': self._check_network(),
            'workspace_check': self._check_workspace(),
            'overall_status': 'healthy'
        }

        # Determine overall status
        if any(not check.get('status') for check in diagnostics.values() if isinstance(check, dict)):
            diagnostics['overall_status'] = 'issues_found'

        return diagnostics

    def _check_environment(self) -> Dict[str, Any]:
        """Check ROS 2 environment variables"""
        checks = {
            'ros_distro': os.environ.get('ROS_DISTRO', 'Not set'),
            'ros_domain_id': os.environ.get('ROS_DOMAIN_ID', '0'),
            'ros_workspace': os.environ.get('ROS_WORKSPACE', 'Not set'),
            'python_path': os.environ.get('PYTHONPATH', 'Not set')
        }

        # Check if ROS 2 is sourced
        try:
            result = subprocess.run(['ros2', '--version'], capture_output=True, text=True)
            ros2_available = result.returncode == 0
        except FileNotFoundError:
            ros2_available = False

        return {
            'checks': checks,
            'ros2_available': ros2_available,
            'status': ros2_available,
            'recommendations': [] if ros2_available else ['Source ROS 2: source /opt/ros/humble/setup.bash']
        }

    def _check_installation(self) -> Dict[str, Any]:
        """Check ROS 2 installation"""
        try:
            result = subprocess.run(['dpkg', '-l', '|', 'grep', 'ros-humble'],
                                  shell=True, capture_output=True, text=True)
            installed = 'ros-humble' in result.stdout
        except:
            installed = False

        return {
            'installed': installed,
            'status': installed,
            'details': result.stdout if installed else 'ROS 2 not found in package manager'
        }

    def _check_network(self) -> Dict[str, Any]:
        """Check ROS 2 network configuration"""
        # Check for multiple ROS domains
        domain_id = os.environ.get('ROS_DOMAIN_ID', '0')

        # Check if localhost is accessible
        try:
            result = subprocess.run(['ping', '-c', '1', 'localhost'],
                                  capture_output=True, text=True)
            localhost_accessible = result.returncode == 0
        except:
            localhost_accessible = False

        return {
            'domain_id': domain_id,
            'localhost_accessible': localhost_accessible,
            'status': localhost_accessible,
            'recommendations': [] if localhost_accessible else ['Check network configuration']
        }

    def _check_workspace(self) -> Dict[str, Any]:
        """Check ROS 2 workspace"""
        workspace_path = os.environ.get('ROS_WORKSPACE', '')

        if workspace_path and os.path.exists(workspace_path):
            # Check if it's a proper ROS workspace
            has_src = os.path.exists(os.path.join(workspace_path, 'src'))
            has_build = os.path.exists(os.path.join(workspace_path, 'build'))
            has_install = os.path.exists(os.path.join(workspace_path, 'install'))

            status = has_src  # At minimum, src directory should exist
        else:
            status = False
            has_src = has_build = has_install = False

        return {
            'workspace_path': workspace_path,
            'has_src': has_src,
            'has_build': has_build,
            'has_install': has_install,
            'status': status
        }

    def generate_troubleshooting_report(self, student_id: str) -> Dict[str, Any]:
        """Generate troubleshooting report for a student"""
        diagnostics = self.run_ros2_diagnostics()

        report = {
            'student_id': student_id,
            'generated_at': datetime.utcnow().isoformat(),
            'diagnostics': diagnostics,
            'recommended_actions': self._generate_recommended_actions(diagnostics),
            'support_level': self._determine_support_level(diagnostics)
        }

        return report

    def _generate_recommended_actions(self, diagnostics: Dict[str, Any]) -> List[str]:
        """Generate recommended actions based on diagnostics"""
        actions = []

        if not diagnostics['environment_check']['ros2_available']:
            actions.append('Source ROS 2 environment: source /opt/ros/humble/setup.bash')

        if not diagnostics['installation_check']['installed']:
            actions.append('Install ROS 2 Humble: sudo apt install ros-humble-desktop-full')

        if not diagnostics['workspace_check']['has_src']:
            actions.append('Initialize ROS workspace: mkdir -p ~/ros2_ws/src && cd ~/ros2_ws')

        return actions

    def _determine_support_level(self, diagnostics: Dict[str, Any]) -> str:
        """Determine required support level"""
        if diagnostics['overall_status'] == 'healthy':
            return 'no_support_needed'
        elif diagnostics['environment_check']['status'] and not diagnostics['workspace_check']['status']:
            return 'low_support'  # Just workspace issues
        else:
            return 'high_support'  # Environment or installation issues

ros2_troubleshooting = ROS2TroubleshootingGuide()
```

#### Simulation Environment Troubleshooting
```python
# simulation_troubleshooting.py
import subprocess
import os
from typing import Dict, List, Any

class SimulationTroubleshootingGuide:
    def __init__(self):
        self.gazebo_issues = {
            'gazebo_not_launching': {
                'symptoms': ['Gazebo fails to start', 'GUI not appearing', 'Segmentation fault'],
                'solutions': [
                    'Check graphics drivers: nvidia-smi (for NVIDIA)',
                    'Set environment: export GAZEBO_GUI_DISABLE_GPU=1',
                    'Check disk space: df -h',
                    'Verify installation: which gz or which gazebo'
                ]
            },
            'models_not_loading': {
                'symptoms': ['Models missing from simulation', '404 errors in console'],
                'solutions': [
                    'Set model path: export GAZEBO_MODEL_PATH=$HOME/.gazebo/models',
                    'Update model database: gz model --update',
                    'Check internet connection for model downloads'
                ]
            },
            'performance_issues': {
                'symptoms': ['Low frame rate', 'Simulation lag', 'High CPU usage'],
                'solutions': [
                    'Reduce physics update rate in world file',
                    'Lower rendering quality: export GAZEBO_RENDER_ENGINE=ogre',
                    'Close other applications to free resources'
                ]
            }
        }

        self.isaac_issues = {
            'isaac_sim_not_starting': {
                'symptoms': ['Isaac Sim fails to launch', 'Python errors', 'CUDA issues'],
                'solutions': [
                    'Verify CUDA installation: nvidia-smi',
                    'Check GPU memory: nvidia-smi -q -d MEMORY',
                    'Install Isaac Sim dependencies: pip install -r requirements.txt'
                ]
            },
            'gpu_memory_errors': {
                'symptoms': ['Out of memory errors', 'CUDA out of memory'],
                'solutions': [
                    'Reduce scene complexity',
                    'Lower texture resolutions',
                    'Close other GPU-intensive applications'
                ]
            }
        }

    def troubleshoot_gazebo(self, error_description: str) -> Dict[str, Any]:
        """Troubleshoot Gazebo-specific issues"""
        for issue, info in self.gazebo_issues.items():
            for symptom in info['symptoms']:
                if symptom.lower() in error_description.lower():
                    return {
                        'issue': issue,
                        'solutions': info['solutions'],
                        'severity': 'high' if 'not_launching' in issue else 'medium'
                    }

        return {
            'issue': 'unknown_gazebo_issue',
            'solutions': [
                'Check Gazebo installation: which gz or which gazebo',
                'Verify graphics drivers',
                'Check system resources',
                'Review Gazebo documentation'
            ],
            'severity': 'unknown'
        }

    def troubleshoot_isaac(self, error_description: str) -> Dict[str, Any]:
        """Troubleshoot Isaac Sim-specific issues"""
        for issue, info in self.isaac_issues.items():
            for symptom in info['symptoms']:
                if symptom.lower() in error_description.lower():
                    return {
                        'issue': issue,
                        'solutions': info['solutions'],
                        'severity': 'high' if 'not_starting' in issue else 'medium'
                    }

        return {
            'issue': 'unknown_isaac_issue',
            'solutions': [
                'Verify Isaac Sim installation',
                'Check GPU compatibility',
                'Review Isaac Sim documentation',
                'Check system requirements'
            ],
            'severity': 'unknown'
        }

    def run_simulation_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive simulation diagnostics"""
        return {
            'gazebo_status': self._check_gazebo_installation(),
            'isaac_status': self._check_isaac_installation(),
            'graphics_status': self._check_graphics_setup(),
            'system_resources': self._check_system_resources()
        }

    def _check_gazebo_installation(self) -> Dict[str, Any]:
        """Check Gazebo installation"""
        try:
            result = subprocess.run(['which', 'gz'], capture_output=True, text=True)
            gz_available = result.returncode == 0

            if not gz_available:
                result = subprocess.run(['which', 'gazebo'], capture_output=True, text=True)
                gazebo_available = result.returncode == 0
            else:
                gazebo_available = False

        except:
            gz_available = gazebo_available = False

        return {
            'gz_available': gz_available,
            'gazebo_available': gazebo_available,
            'status': gz_available or gazebo_available
        }

    def _check_isaac_installation(self) -> Dict[str, Any]:
        """Check Isaac Sim installation"""
        try:
            # Check if Isaac Sim Python package is available
            import omni
            isaac_available = True
        except ImportError:
            isaac_available = False

        return {
            'isaac_available': isaac_available,
            'status': isaac_available
        }

    def _check_graphics_setup(self) -> Dict[str, Any]:
        """Check graphics setup"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            nvidia_gpu = result.returncode == 0
        except:
            nvidia_gpu = False

        try:
            result = subprocess.run(['lspci', '|', 'grep', '-i', 'vga'],
                                  shell=True, capture_output=True, text=True)
            has_gpu = len(result.stdout) > 0
        except:
            has_gpu = False

        return {
            'nvidia_gpu': nvidia_gpu,
            'has_gpu': has_gpu,
            'opengl_available': self._check_opengl()
        }

    def _check_opengl(self) -> bool:
        """Check OpenGL availability"""
        try:
            result = subprocess.run(['glxinfo', '|', 'grep', 'OpenGL'],
                                  shell=True, capture_output=True, text=True)
            return 'OpenGL' in result.stdout
        except:
            return False

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        import psutil

        return {
            'cpu_count': psutil.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_space_gb': round(psutil.disk_usage('/').free / (1024**3), 2),
            'memory_percent': psutil.virtual_memory().percent
        }

simulation_troubleshooting = SimulationTroubleshootingGuide()
```

### 2. Student Support Systems

#### Office Hours and Support Queue
```python
# support_system.py
from datetime import datetime, timedelta
from typing import Dict, List, Any
import heapq

class SupportSystem:
    def __init__(self):
        self.support_tickets = []
        self.office_hours = {
            'monday': {'start': '10:00', 'end': '12:00'},
            'wednesday': {'start': '14:00', 'end': '16:00'},
            'friday': {'start': '15:00', 'end': '17:00'}
        }
        self.ta_schedule = [
            {'name': 'TA 1', 'availability': ['monday', 'tuesday']},
            {'name': 'TA 2', 'availability': ['wednesday', 'thursday']},
            {'name': 'TA 3', 'availability': ['friday', 'saturday']}
        ]

    def create_support_ticket(self, student_id: str, issue_type: str, description: str,
                            priority: str = 'medium') -> str:
        """Create a support ticket for a student"""
        ticket_id = f"ticket_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{student_id[:4]}"

        ticket = {
            'ticket_id': ticket_id,
            'student_id': student_id,
            'issue_type': issue_type,
            'description': description,
            'priority': priority,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'open',
            'assigned_ta': None,
            'estimated_wait': self._calculate_wait_time(priority),
            'category': self._categorize_issue(issue_type)
        }

        # Add to priority queue based on priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        heapq.heappush(self.support_tickets, (priority_order[priority], ticket))

        return ticket_id

    def _calculate_wait_time(self, priority: str) -> str:
        """Calculate estimated wait time based on priority"""
        wait_times = {
            'high': '15-30 minutes',
            'medium': '1-2 hours',
            'low': '4-8 hours'
        }
        return wait_times.get(priority, '2-4 hours')

    def _categorize_issue(self, issue_type: str) -> str:
        """Categorize the issue for proper routing"""
        technical_keywords = ['ros', 'gazebo', 'isaac', 'simulation', 'build', 'install', 'error', 'crash']
        conceptual_keywords = ['understand', 'confused', 'concept', 'algorithm', 'theory', 'how to']
        assignment_keywords = ['assignment', 'exercise', 'project', 'grade', 'submission']

        issue_lower = issue_type.lower()

        if any(keyword in issue_lower for keyword in technical_keywords):
            return 'technical'
        elif any(keyword in issue_lower for keyword in conceptual_keywords):
            return 'conceptual'
        elif any(keyword in issue_lower for keyword in assignment_keywords):
            return 'assignment'
        else:
            return 'general'

    def get_next_support_slot(self) -> Dict[str, Any]:
        """Get the next available support slot"""
        now = datetime.utcnow()

        # Find next available office hours
        current_weekday = now.strftime('%A').lower()

        # Check if today has office hours and if we're within the time window
        if current_weekday in self.office_hours:
            start_time = datetime.strptime(self.office_hours[current_weekday]['start'], '%H:%M').time()
            end_time = datetime.strptime(self.office_hours[current_weekday]['end'], '%H:%M').time()

            if start_time <= now.time() <= end_time:
                return {
                    'available': True,
                    'time': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'office_hours'
                }

        # Find next office hours
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_idx = weekdays.index(current_weekday)

        for i in range(1, 8):
            next_idx = (current_idx + i) % 7
            next_day = weekdays[next_idx]

            if next_day in self.office_hours:
                next_date = now + timedelta(days=i)
                start_time = self.office_hours[next_day]['start']
                return {
                    'available': True,
                    'time': f"{next_date.strftime('%Y-%m-%d')} {start_time}",
                    'type': 'office_hours'
                }

        return {'available': False, 'message': 'No office hours scheduled'}

    def assign_ta_to_ticket(self, ticket_id: str) -> bool:
        """Assign a TA to a support ticket"""
        # Find the ticket
        ticket = self._find_ticket(ticket_id)
        if not ticket:
            return False

        # Find available TA based on category and availability
        available_ta = self._find_available_ta(ticket['category'])

        if available_ta:
            ticket['assigned_ta'] = available_ta
            ticket['status'] = 'assigned'
            return True

        return False

    def _find_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Find a ticket by ID"""
        for priority, ticket in self.support_tickets:
            if ticket['ticket_id'] == ticket_id:
                return ticket
        return None

    def _find_available_ta(self, category: str) -> str:
        """Find an available TA for the category"""
        # Simple assignment logic - in reality, you'd want more sophisticated scheduling
        import random
        available_tas = [ta['name'] for ta in self.ta_schedule]
        return random.choice(available_tas) if available_tas else None

    def get_support_queue_status(self) -> Dict[str, Any]:
        """Get current support queue status"""
        queue_by_priority = {'high': 0, 'medium': 0, 'low': 0}
        queue_by_category = {'technical': 0, 'conceptual': 0, 'assignment': 0, 'general': 0}

        for priority, ticket in self.support_tickets:
            queue_by_priority[ticket['priority']] += 1
            queue_by_category[ticket['category']] += 1

        return {
            'total_tickets': len(self.support_tickets),
            'by_priority': queue_by_priority,
            'by_category': queue_by_category,
            'average_wait_time': self._calculate_average_wait(),
            'next_available_slot': self.get_next_support_slot()
        }

    def _calculate_average_wait(self) -> str:
        """Calculate average wait time"""
        # Simplified calculation
        if len(self.support_tickets) == 0:
            return 'No tickets in queue'
        elif len(self.support_tickets) < 5:
            return '15-30 minutes'
        elif len(self.support_tickets) < 15:
            return '30-60 minutes'
        else:
            return '1-2 hours'

    def generate_support_report(self) -> Dict[str, Any]:
        """Generate comprehensive support report"""
        return {
            'report_generated_at': datetime.utcnow().isoformat(),
            'queue_status': self.get_support_queue_status(),
            'office_hours_schedule': self.office_hours,
            'ta_availability': self.ta_schedule,
            'recent_tickets': self._get_recent_tickets(),
            'support_metrics': self._calculate_support_metrics()
        }

    def _get_recent_tickets(self) -> List[Dict[str, Any]]:
        """Get recently created tickets"""
        # Get the 5 most recent tickets
        recent = []
        for priority, ticket in sorted(self.support_tickets, key=lambda x: x[1]['created_at'], reverse=True)[:5]:
            recent.append({
                'ticket_id': ticket['ticket_id'],
                'student_id': ticket['student_id'],
                'issue_type': ticket['issue_type'],
                'priority': ticket['priority'],
                'status': ticket['status'],
                'created_at': ticket['created_at']
            })
        return recent

    def _calculate_support_metrics(self) -> Dict[str, Any]:
        """Calculate support metrics"""
        if not self.support_tickets:
            return {
                'average_resolution_time': 'N/A',
                'satisfaction_rate': 'N/A',
                'ticket_backlog': 0
            }

        # Simplified metrics calculation
        return {
            'average_resolution_time': '45 minutes',
            'satisfaction_rate': '85%',
            'ticket_backlog': len(self.support_tickets)
        }

support_system = SupportSystem()
```

## Best Practices and Guidelines

### 1. Teaching Best Practices

#### Effective Teaching Strategies for Robotics
```python
# teaching_best_practices.py
from typing import Dict, List, Any

class TeachingBestPractices:
    def __init__(self):
        self.practice_categories = {
            'conceptual_understanding': {
                'name': 'Conceptual Understanding',
                'strategies': [
                    {
                        'name': 'Analogies and Metaphors',
                        'description': 'Use everyday analogies to explain complex robotics concepts',
                        'example': 'Compare ROS nodes to people in a conversation - each has a role and communicates with others',
                        'implementation': 'Start each new concept with a real-world analogy before diving into technical details'
                    },
                    {
                        'name': 'Progressive Complexity',
                        'description': 'Build concepts from simple to complex incrementally',
                        'example': 'Start with simple publisher/subscriber, then add services, then actions',
                        'implementation': 'Ensure each concept builds on the previous one with clear connections'
                    },
                    {
                        'name': 'Visual Learning',
                        'description': 'Use diagrams, flowcharts, and visual representations',
                        'example': 'Show ROS graph visualization, system architecture diagrams',
                        'implementation': 'Include visual aids in all lectures and provide interactive diagrams'
                    }
                ]
            },
            'hands_on_learning': {
                'name': 'Hands-On Learning',
                'strategies': [
                    {
                        'name': 'Incremental Building',
                        'description': 'Have students build projects incrementally',
                        'example': 'Start with basic robot movement, add sensors, then AI integration',
                        'implementation': 'Break complex projects into smaller, achievable milestones'
                    },
                    {
                        'name': 'Debugging Skills',
                        'description': 'Teach systematic debugging approaches',
                        'example': 'ROS 2 debugging tools, Gazebo simulation debugging',
                        'implementation': 'Dedicate time to debugging workshops and common issue resolution'
                    },
                    {
                        'name': 'Real-World Applications',
                        'description': 'Connect concepts to real-world robotics applications',
                        'example': 'Show how navigation stacks work in delivery robots',
                        'implementation': 'Include case studies and industry examples throughout the course'
                    }
                ]
            },
            'collaborative_learning': {
                'name': 'Collaborative Learning',
                'strategies': [
                    {
                        'name': 'Peer Programming',
                        'description': 'Encourage students to work in pairs on complex problems',
                        'example': 'ROS package development in pairs with defined roles',
                        'implementation': 'Structure assignments to encourage collaboration and peer review'
                    },
                    {
                        'name': 'Study Groups',
                        'description': 'Facilitate formation of study groups',
                        'example': 'Topic-specific study groups for different modules',
                        'implementation': 'Provide study spaces and discussion forums for group formation'
                    },
                    {
                        'name': 'Peer Review',
                        'description': 'Implement structured peer review processes',
                        'example': 'Code review between students with structured rubrics',
                        'implementation': 'Train students on giving and receiving constructive feedback'
                    }
                ]
            }
        }

    def get_teaching_strategies(self, category: str = None) -> Dict[str, Any]:
        """Get teaching strategies, optionally filtered by category"""
        if category and category in self.practice_categories:
            return {category: self.practice_categories[category]}
        else:
            return self.practice_categories

    def suggest_lecture_structure(self, topic: str) -> Dict[str, Any]:
        """Suggest an effective lecture structure for a robotics topic"""
        base_structure = {
            'duration': '90 minutes',
            'components': [
                {
                    'name': 'Warm-up Activity',
                    'duration': '10 minutes',
                    'description': 'Quick review or thought experiment related to the topic'
                },
                {
                    'name': 'Concept Introduction',
                    'duration': '25 minutes',
                    'description': 'Introduce new concepts with analogies and visual aids'
                },
                {
                    'name': 'Hands-On Activity',
                    'duration': '30 minutes',
                    'description': 'Practical exercise implementing the concepts'
                },
                {
                    'name': 'Group Discussion',
                    'duration': '15 minutes',
                    'description': 'Students share results and discuss challenges'
                },
                {
                    'name': 'Wrap-up and Q&A',
                    'duration': '10 minutes',
                    'description': 'Summarize key points and address questions'
                }
            ]
        }

        # Customize based on topic
        if 'simulation' in topic.lower():
            base_structure['components'][2]['description'] = 'Hands-on simulation exercise with Gazebo or Isaac Sim'
        elif 'ros' in topic.lower():
            base_structure['components'][2]['description'] = 'Practical ROS 2 exercise with nodes and communication'
        elif 'ai' in topic.lower():
            base_structure['components'][2]['description'] = 'AI integration exercise with perception or planning'

        return base_structure

    def recommend_assignment_types(self, module: str) -> List[Dict[str, Any]]:
        """Recommend assignment types for different modules"""
        recommendations = {
            'module_1': [  # ROS 2 Fundamentals
                {
                    'type': 'coding_exercise',
                    'name': 'ROS 2 Publisher/Subscriber',
                    'complexity': 'beginner',
                    'learning_objectives': ['Node communication', 'Message passing', 'Topic architecture'],
                    'estimated_time': '3-4 hours',
                    'collaboration_level': 'individual'
                },
                {
                    'type': 'debugging_challenge',
                    'name': 'ROS 2 Communication Issues',
                    'complexity': 'intermediate',
                    'learning_objectives': ['Troubleshooting', 'Network configuration', 'Error resolution'],
                    'estimated_time': '2-3 hours',
                    'collaboration_level': 'pair'
                }
            ],
            'module_2': [  # Simulation
                {
                    'type': 'simulation_project',
                    'name': 'Custom World Creation',
                    'complexity': 'intermediate',
                    'learning_objectives': ['Environment design', 'Physics configuration', 'Model integration'],
                    'estimated_time': '6-8 hours',
                    'collaboration_level': 'team'
                },
                {
                    'type': 'integration_task',
                    'name': 'ROS-Simulation Bridge',
                    'complexity': 'advanced',
                    'learning_objectives': ['System integration', 'Realistic simulation', 'Performance optimization'],
                    'estimated_time': '8-10 hours',
                    'collaboration_level': 'team'
                }
            ],
            'module_3': [  # AI Integration
                {
                    'type': 'ai_integration',
                    'name': 'Perception System',
                    'complexity': 'advanced',
                    'learning_objectives': ['Computer vision', 'Sensor processing', 'AI model integration'],
                    'estimated_time': '10-12 hours',
                    'collaboration_level': 'team'
                },
                {
                    'type': 'planning_algorithm',
                    'name': 'Path Planning',
                    'complexity': 'advanced',
                    'learning_objectives': ['Algorithm implementation', 'Optimization', 'Real-time constraints'],
                    'estimated_time': '8-10 hours',
                    'collaboration_level': 'pair'
                }
            ],
            'module_4': [  # Voice Control
                {
                    'type': 'voice_integration',
                    'name': 'Voice-to-Action System',
                    'complexity': 'advanced',
                    'learning_objectives': ['Speech recognition', 'NLP', 'System integration'],
                    'estimated_time': '12-15 hours',
                    'collaboration_level': 'team'
                },
                {
                    'type': 'capstone_project',
                    'name': 'Autonomous Humanoid Robot',
                    'complexity': 'advanced',
                    'learning_objectives': ['Full system integration', 'Advanced robotics', 'Project management'],
                    'estimated_time': '40-50 hours',
                    'collaboration_level': 'team'
                }
            ]
        }

        return recommendations.get(module, recommendations['module_1'])

    def provide_assessment_guidance(self) -> Dict[str, Any]:
        """Provide guidance for assessing robotics students"""
        return {
            'assessment_types': [
                {
                    'type': 'practical_exam',
                    'description': 'Hands-on coding and debugging session',
                    'weight': 0.30,
                    'benefits': ['Direct skill assessment', 'Real-time problem solving', 'Immediate feedback'],
                    'considerations': ['Requires significant setup', 'Subjective grading possible']
                },
                {
                    'type': 'project_portfolio',
                    'description': 'Collection of completed projects with documentation',
                    'weight': 0.35,
                    'benefits': ['Shows progression', 'Includes documentation skills', 'Demonstrates integration'],
                    'considerations': ['Time-intensive to grade', 'Requires rubric standardization']
                },
                {
                    'type': 'peer_evaluation',
                    'description': 'Student evaluation of teammates and code',
                    'weight': 0.10,
                    'benefits': ['Develops critical thinking', 'Encourages collaboration', 'Additional feedback'],
                    'considerations': ['May be biased', 'Requires training on evaluation']
                },
                {
                    'type': 'technical_interview',
                    'description': 'One-on-one discussion of concepts and projects',
                    'weight': 0.15,
                    'benefits': ['Deep understanding check', 'Personalized feedback', 'Conceptual clarity'],
                    'considerations': ['Time-intensive', 'May cause anxiety', 'Requires scheduling']
                },
                {
                    'type': 'reflection_paper',
                    'description': 'Written reflection on learning and challenges',
                    'weight': 0.10,
                    'benefits': ['Metacognitive skills', 'Writing practice', 'Personal insights'],
                    'considerations': ['Subjective', 'May not reflect technical skills']
                }
            ],
            'grading_considerations': [
                'Weight practical skills more heavily than theoretical knowledge',
                'Include collaboration and communication skills in team projects',
                'Consider effort and improvement over time, not just final results',
                'Provide multiple opportunities for students to demonstrate learning',
                'Use detailed rubrics to ensure consistent grading'
            ]
        }

    def suggest_inclusive_teaching_practices(self) -> List[Dict[str, Any]]:
        """Suggest inclusive teaching practices for diverse student populations"""
        return [
            {
                'practice': 'Multiple Representation Modes',
                'description': 'Present concepts through different modalities (visual, auditory, kinesthetic)',
                'implementation': 'Provide videos, diagrams, hands-on activities, and detailed explanations for each concept'
            },
            {
                'practice': 'Flexible Assessment Options',
                'description': 'Offer different ways for students to demonstrate knowledge',
                'implementation': 'Allow students to choose between coding projects, written explanations, or presentations'
            },
            {
                'practice': 'Cultural Relevance',
                'description': 'Connect robotics concepts to diverse cultural contexts',
                'implementation': 'Use examples from different cultural robotics applications and industries worldwide'
            },
            {
                'practice': 'Accommodation for Disabilities',
                'description': 'Provide accommodations for students with disabilities',
                'implementation': 'Offer screen reader compatible materials, extended time for practical exams, alternative input methods'
            },
            {
                'practice': 'Language Support',
                'description': 'Support students for whom English is not their first language',
                'implementation': 'Provide glossaries of technical terms, allow use of translation tools, offer extra explanation time'
            }
        ]

teaching_best_practices = TeachingBestPractices()
```

### 2. Assessment and Grading Guidelines

#### Rubric Development and Grading Standards
```python
# assessment_guidelines.py
from typing import Dict, List, Any

class AssessmentGuidelines:
    def __init__(self):
        self.rubric_templates = {
            'coding_assignment': {
                'criteria': [
                    {
                        'name': 'Functionality',
                        'description': 'Does the code work as intended?',
                        'weight': 40,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Code works perfectly with no bugs, handles all edge cases'},
                            'good': {'score': 3, 'description': 'Code works with minor issues, handles most cases'},
                            'satisfactory': {'score': 2, 'description': 'Code works but has some bugs or missing features'},
                            'needs_improvement': {'score': 1, 'description': 'Code has significant issues or doesn\'t work properly'},
                            'unsatisfactory': {'score': 0, 'description': 'Code doesn\'t work or is incomplete'}
                        }
                    },
                    {
                        'name': 'Code Quality',
                        'description': 'Is the code well-structured and readable?',
                        'weight': 25,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Excellent structure, clear variable names, proper documentation'},
                            'good': {'score': 3, 'description': 'Good structure with minor readability issues'},
                            'satisfactory': {'score': 2, 'description': 'Basic structure but could be improved'},
                            'needs_improvement': {'score': 1, 'description': 'Poor structure and readability'},
                            'unsatisfactory': {'score': 0, 'description': 'Unreadable or disorganized code'}
                        }
                    },
                    {
                        'name': 'ROS 2 Best Practices',
                        'description': 'Does the code follow ROS 2 conventions?',
                        'weight': 20,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Perfect use of ROS 2 patterns, proper node design, good error handling'},
                            'good': {'score': 3, 'description': 'Good use of ROS 2 patterns with minor issues'},
                            'satisfactory': {'score': 2, 'description': 'Basic ROS 2 usage but could follow conventions better'},
                            'needs_improvement': {'score': 1, 'description': 'Poor ROS 2 implementation'},
                            'unsatisfactory': {'score': 0, 'description': 'Does not follow ROS 2 best practices'}
                        }
                    },
                    {
                        'name': 'Documentation',
                        'description': 'Is the code properly documented?',
                        'weight': 15,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Comprehensive documentation, clear comments, usage examples'},
                            'good': {'score': 3, 'description': 'Good documentation with minor gaps'},
                            'satisfactory': {'score': 2, 'description': 'Basic documentation present'},
                            'needs_improvement': {'score': 1, 'description': 'Minimal or unclear documentation'},
                            'unsatisfactory': {'score': 0, 'description': 'No documentation'}
                        }
                    }
                ]
            },
            'simulation_project': {
                'criteria': [
                    {
                        'name': 'Simulation Quality',
                        'description': 'Is the simulation realistic and well-designed?',
                        'weight': 35,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Highly realistic physics, detailed models, smooth performance'},
                            'good': {'score': 3, 'description': 'Good physics and design with minor issues'},
                            'satisfactory': {'score': 2, 'description': 'Basic simulation with some problems'},
                            'needs_improvement': {'score': 1, 'description': 'Poor simulation quality'},
                            'unsatisfactory': {'score': 0, 'description': 'Simulation doesn\'t work properly'}
                        }
                    },
                    {
                        'name': 'ROS Integration',
                        'description': 'How well does the simulation integrate with ROS?',
                        'weight': 30,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Seamless integration, proper sensor simulation, realistic communication'},
                            'good': {'score': 3, 'description': 'Good integration with minor issues'},
                            'satisfactory': {'score': 2, 'description': 'Basic integration present'},
                            'needs_improvement': {'score': 1, 'description': 'Poor integration'},
                            'unsatisfactory': {'score': 0, 'description': 'No proper ROS integration'}
                        }
                    },
                    {
                        'name': 'Creativity and Innovation',
                        'description': 'Does the project show creative thinking?',
                        'weight': 20,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Highly innovative approach, creative problem solving'},
                            'good': {'score': 3, 'description': 'Good creative elements'},
                            'satisfactory': {'score': 2, 'description': 'Some creative thinking present'},
                            'needs_improvement': {'score': 1, 'description': 'Little creativity shown'},
                            'unsatisfactory': {'score': 0, 'description': 'No creative elements'}
                        }
                    },
                    {
                        'name': 'Documentation and Presentation',
                        'description': 'Is the project well-documented and presented?',
                        'weight': 15,
                        'levels': {
                            'excellent': {'score': 4, 'description': 'Comprehensive documentation, clear presentation, easy to understand'},
                            'good': {'score': 3, 'description': 'Good documentation with minor gaps'},
                            'satisfactory': {'score': 2, 'description': 'Basic documentation present'},
                            'needs_improvement': {'score': 1, 'description': 'Poor documentation'},
                            'unsatisfactory': {'score': 0, 'description': 'No documentation'}
                        }
                    }
                ]
            }
        }

    def create_assignment_rubric(self, assignment_type: str, custom_criteria: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a rubric for an assignment"""
        if assignment_type in self.rubric_templates:
            template = self.rubric_templates[assignment_type]
            if custom_criteria:
                # Merge custom criteria with template
                template['criteria'].extend(custom_criteria)

            return {
                'assignment_type': assignment_type,
                'criteria': template['criteria'],
                'total_points': sum(c['weight'] for c in template['criteria']),
                'created_at': datetime.utcnow().isoformat(),
                'last_modified': datetime.utcnow().isoformat()
            }
        else:
            return None

    def grade_submission(self, submission: Dict[str, Any], rubric: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a submission using a rubric"""
        total_score = 0
        max_possible = 0
        detailed_scores = {}

        for criterion in rubric['criteria']:
            criterion_name = criterion['name']
            criterion_weight = criterion['weight']
            max_possible += criterion_weight

            # Get the score for this criterion from the submission
            # In practice, this would involve TA evaluation
            criterion_score = submission.get(f"score_{criterion_name.replace(' ', '_').lower()}", 0)

            # Normalize the score based on the criterion's level system
            normalized_score = self._normalize_criterion_score(criterion_score, criterion['levels'])

            weighted_score = (normalized_score / 4) * criterion_weight  # 4 is max level score
            total_score += weighted_score

            detailed_scores[criterion_name] = {
                'raw_score': criterion_score,
                'normalized_score': normalized_score,
                'weighted_score': round(weighted_score, 2),
                'weight': criterion_weight
            }

        percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0

        return {
            'submission_id': submission.get('submission_id'),
            'student_id': submission.get('student_id'),
            'total_score': round(total_score, 2),
            'max_possible': max_possible,
            'percentage': round(percentage, 2),
            'letter_grade': self._percentage_to_letter(percentage),
            'detailed_scores': detailed_scores,
            'graded_at': datetime.utcnow().isoformat(),
            'grader_id': submission.get('grader_id')
        }

    def _normalize_criterion_score(self, raw_score: int, levels: Dict[str, Dict[str, Any]]) -> int:
        """Normalize raw score to the 0-4 scale based on levels"""
        # In a real implementation, this would map the TA's level selection to a numeric score
        # For this example, we'll assume the raw_score is already the level score (0-4)
        return min(max(raw_score, 0), 4)

    def _percentage_to_letter(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 97: return 'A+'
        elif percentage >= 93: return 'A'
        elif percentage >= 90: return 'A-'
        elif percentage >= 87: return 'B+'
        elif percentage >= 83: return 'B'
        elif percentage >= 80: return 'B-'
        elif percentage >= 77: return 'C+'
        elif percentage >= 73: return 'C'
        elif percentage >= 70: return 'C-'
        elif percentage >= 60: return 'D'
        else: return 'F'

    def provide_grading_consistency_tips(self) -> List[str]:
        """Provide tips for maintaining grading consistency"""
        return [
            "Use detailed rubrics with specific criteria and examples",
            "Grade all submissions for one criterion before moving to the next",
            "Double-check grades that seem significantly different from the norm",
            "Have another TA or instructor review a sample of grades",
            "Calibrate grading by reviewing a few submissions together as a team",
            "Provide specific, actionable feedback for each criterion",
            "Document grading decisions for consistency across assignments",
            "Use grade distribution analytics to identify potential inconsistencies"
        ]

    def generate_grading_worksheet(self, assignment_id: str, student_count: int) -> Dict[str, Any]:
        """Generate a grading worksheet for TAs"""
        return {
            'worksheet_id': f"grading_ws_{assignment_id}_{datetime.utcnow().strftime('%Y%m%d')}",
            'assignment_id': assignment_id,
            'student_count': student_count,
            'criteria': self.rubric_templates.get('coding_assignment', {}).get('criteria', []),
            'grading_deadline': (datetime.utcnow() + timedelta(days=7)).isoformat(),
            'instructions': [
                'Grade each criterion independently',
                'Use the full range of scores (0-4)',
                'Provide specific feedback for each criterion',
                'Check for consistency across similar submissions',
                'Submit grades by the deadline'
            ],
            'created_at': datetime.utcnow().isoformat()
        }

assessment_guidelines = AssessmentGuidelines()
```

This comprehensive instructor and TA documentation provides:

1. **Course Administration**: Setup procedures, dashboards, and management tools
2. **Student Management**: Enrollment, progress tracking, and reporting systems
3. **Grading Systems**: Automated grading, rubrics, and assessment tools
4. **Technical Support**: Troubleshooting guides for ROS 2, Gazebo, and Isaac Sim
5. **Support Systems**: Ticket management and student support workflows
6. **Teaching Best Practices**: Strategies for effective robotics education
7. **Assessment Guidelines**: Rubrics and grading standards

The documentation is designed to support instructors and TAs in delivering a high-quality educational experience while providing systematic approaches to student support, technical troubleshooting, and course management.

Last updated: December 13, 2025