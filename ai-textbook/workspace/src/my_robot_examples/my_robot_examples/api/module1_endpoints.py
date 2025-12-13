#!/usr/bin/env python3
"""
API endpoints for Module 1 progress tracking and exercise validation
"""

from flask import Flask, jsonify, request
import json
import os
from datetime import datetime


class Module1API:
    """
    API endpoints for Module 1 (ROS 2 Fundamentals) progress tracking and validation.
    """

    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize the API with a Flask app."""
        self.register_routes(app)

    def register_routes(self, app: Flask):
        """Register the API routes."""

        @app.route('/api/v1/module1/progress', methods=['GET'])
        def get_module1_progress():
            """Get progress information for Module 1."""
            student_id = request.args.get('student_id')

            if not student_id:
                return jsonify({'error': 'student_id parameter is required'}), 400

            # In a real implementation, this would fetch from a database
            # For now, return mock data
            progress_data = {
                'student_id': student_id,
                'module_id': 'module-1-ros2',
                'module_name': 'ROS 2 Fundamentals',
                'completion_percentage': 0.0,  # Would be calculated from completed exercises
                'completed_chapters': [],
                'completed_exercises': [],
                'assessment_score': None,
                'last_accessed': datetime.now().isoformat()
            }

            return jsonify(progress_data)

        @app.route('/api/v1/module1/exercise/submit', methods=['POST'])
        def submit_exercise():
            """Submit an exercise for validation."""
            data = request.json

            if not data or 'exercise_id' not in data or 'student_id' not in data or 'solution' not in data:
                return jsonify({'error': 'exercise_id, student_id, and solution are required'}), 400

            exercise_id = data['exercise_id']
            student_id = data['student_id']
            solution = data['solution']

            # In a real implementation, this would validate the solution
            # For now, return mock validation result
            validation_result = {
                'exercise_id': exercise_id,
                'student_id': student_id,
                'passed': True,  # Would be determined by actual validation
                'feedback': f'Exercise {exercise_id} submitted successfully by student {student_id}',
                'timestamp': datetime.now().isoformat()
            }

            return jsonify(validation_result)

        @app.route('/api/v1/module1/exercise/validate', methods=['POST'])
        def validate_exercise():
            """Validate an exercise solution without storing it."""
            data = request.json

            if not data or 'exercise_id' not in data or 'solution' not in data:
                return jsonify({'error': 'exercise_id and solution are required'}), 400

            exercise_id = data['exercise_id']
            solution = data['solution']

            # In a real implementation, this would run actual validation
            # For now, return mock validation result
            validation_result = {
                'exercise_id': exercise_id,
                'passed': True,  # Would be determined by actual validation
                'feedback': f'Validation passed for exercise {exercise_id}',
                'details': [
                    'All requirements met',
                    'Code follows best practices',
                    'Proper error handling implemented'
                ],
                'timestamp': datetime.now().isoformat()
            }

            return jsonify(validation_result)

        @app.route('/api/v1/module1/status', methods=['GET'])
        def module1_status():
            """Get status of Module 1 implementation."""
            status = {
                'module': 'Module 1: ROS 2 Fundamentals',
                'status': 'implemented',
                'chapters_available': 5,
                'exercises_available': 5,
                'api_endpoints': [
                    '/api/v1/module1/progress',
                    '/api/v1/module1/exercise/submit',
                    '/api/v1/module1/exercise/validate'
                ],
                'last_updated': datetime.now().isoformat()
            }

            return jsonify(status)


# For standalone testing
if __name__ == '__main__':
    app = Flask(__name__)
    api = Module1API(app)

    print("Module 1 API endpoints available:")
    print("- GET /api/v1/module1/progress?student_id=X")
    print("- POST /api/v1/module1/exercise/submit")
    print("- POST /api/v1/module1/exercise/validate")
    print("- GET /api/v1/module1/status")

    app.run(debug=True, port=5001)