#!/usr/bin/env python3
"""
Main API for the Physical AI & Humanoid Robotics Course
Combines all module-specific APIs into a single interface
"""

from flask import Flask, request
from .module1_endpoints import Module1API
from .module2_endpoints import Module2API
from .module4_endpoints import Module4API
import json
from datetime import datetime


class MainAPI:
    """
    Main API class that combines all module-specific APIs
    """

    def __init__(self):
        self.app = Flask(__name__)
        self.module1_api = Module1API()
        self.module2_api = Module2API()
        self.module4_api = Module4API()

        # Initialize all APIs with the main Flask app
        self.module1_api.init_app(self.app)
        self.module2_api.init_app(self.app)
        self.module4_api.init_app(self.app)

        # Register main routes
        self.register_main_routes()

    def register_main_routes(self):
        """Register main API routes that span multiple modules"""

        @self.app.route('/api/v1/progress/overall', methods=['GET'])
        def get_overall_progress():
            """Get overall progress across all modules."""
            student_id = request.args.get('student_id')

            if not student_id:
                return jsonify({'error': 'student_id parameter is required'}), 400

            # This would aggregate progress from all modules in a real implementation
            overall_progress = {
                'student_id': student_id,
                'overall_completion': 0.0,
                'modules_progress': {
                    'module-1-ros2': 0.0,
                    'module-2-simulation': 0.0,
                    'module-3-isaac': 0.0,
                    'module-4-vla': 0.0
                },
                'total_exercises_completed': 0,
                'total_labs_completed': 0,
                'total_simulation_hours': 0.0,
                'capstone_status': 'not_started',
                'last_accessed': datetime.now().isoformat()
            }

            return jsonify(overall_progress)

        @self.app.route('/api/v1/status', methods=['GET'])
        def get_course_status():
            """Get overall course API status."""
            status = {
                'course': 'Physical AI & Humanoid Robotics',
                'status': 'operational',
                'modules_supported': ['module-1-ros2', 'module-2-simulation', 'module-4-vla'],
                'total_api_endpoints': 17,  # Count of all endpoints
                'version': '1.0.0',
                'last_updated': datetime.now().isoformat()
            }

            return jsonify(status)


def create_app():
    """Factory function to create the Flask app."""
    main_api = MainAPI()
    return main_api.app


# For standalone testing
if __name__ == '__main__':
    from flask import request  # Import here to avoid circular import issues

    main_api = MainAPI()

    print("Physical AI & Humanoid Robotics Course API")
    print("Available Endpoints:")
    print("\nModule 1 (ROS 2 Fundamentals):")
    print("- GET /api/v1/module1/progress?student_id=X")
    print("- POST /api/v1/module1/exercise/submit")
    print("- POST /api/v1/module1/exercise/validate")
    print("- GET /api/v1/module1/status")

    print("\nModule 2 (Simulation Environments):")
    print("- GET /api/v1/module2/progress?student_id=X")
    print("- POST /api/v1/module2/exercise/submit")
    print("- POST /api/v1/module2/exercise/validate")
    print("- GET /api/v1/module2/simulation/metrics?student_id=X")
    print("- GET /api/v1/module2/status")

    print("\nModule 4 (Voice-Controlled Robotics):")
    print("- GET /api/v1/module4/progress?student_id=X")
    print("- POST /api/v1/module4/lab/submit")
    print("- POST /api/v1/module4/lab/validate")
    print("- POST /api/v1/module4/capstone/progress")
    print("- POST /api/v1/module4/capstone/submit")
    print("- GET /api/v1/module4/capstone/status")
    print("- GET /api/v1/module4/status")

    print("\nOverall Course:")
    print("- GET /api/v1/progress/overall?student_id=X")
    print("- GET /api/v1/status")

    main_api.app.run(debug=True, port=5000)