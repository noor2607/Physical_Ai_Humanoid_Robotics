#!/usr/bin/env python3
"""
Core validation framework for the Physical AI & Humanoid Robotics course
"""
import os
import sys
import json
import yaml
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import psutil


class ValidationResult:
    """Represents the result of a validation operation"""
    def __init__(self, status: str, message: str, score: float = 0.0, details: Optional[Dict] = None):
        self.status = status  # 'pass', 'fail', 'error'
        self.message = message
        self.score = score
        self.details = details or {}
        self.timestamp = time.time()

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "status": self.status,
            "message": self.message,
            "score": self.score,
            "details": self.details,
            "timestamp": self.timestamp
        }


class BaseValidator:
    """Base class for all validators"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def validate(self, submission_path: str) -> ValidationResult:
        """Validate a submission - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement validate method")

    def check_file_exists(self, path: str) -> bool:
        """Check if a file exists"""
        return os.path.exists(path)

    def check_directory_exists(self, path: str) -> bool:
        """Check if a directory exists"""
        return os.path.exists(path) and os.path.isdir(path)

    def load_module_from_file(self, module_name: str, file_path: str):
        """Load a Python module from a file path"""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


class ROS2Validator(BaseValidator):
    """Validator for ROS 2 related exercises"""
    def __init__(self):
        super().__init__("ROS2 Validator", "Validates ROS 2 package structure and functionality")

    def validate(self, submission_path: str) -> ValidationResult:
        """Validate a ROS 2 package submission"""
        try:
            # Check if package.xml exists
            package_xml_path = os.path.join(submission_path, "package.xml")
            if not self.check_file_exists(package_xml_path):
                return ValidationResult("fail", "Missing package.xml file", 0.0)

            # Check if CMakeLists.txt exists
            cmake_path = os.path.join(submission_path, "CMakeLists.txt")
            if not self.check_file_exists(cmake_path):
                return ValidationResult("fail", "Missing CMakeLists.txt file", 0.0)

            # Try to build the package (if in a ROS 2 workspace)
            try:
                result = subprocess.run([
                    'colcon', 'build', '--packages-select', os.path.basename(submission_path)
                ], capture_output=True, text=True, timeout=60)

                if result.returncode != 0:
                    return ValidationResult("fail", f"Build failed: {result.stderr}", 0.0)
            except subprocess.TimeoutExpired:
                return ValidationResult("error", "Build timed out", 0.0)
            except FileNotFoundError:
                # colcon not available, skip build test
                pass

            # Check for common ROS 2 file patterns
            python_files = [f for f in os.listdir(submission_path) if f.endswith('.py')]
            if not python_files:
                return ValidationResult("fail", "No Python files found in package", 30.0)

            # Basic code structure validation
            score = 50.0
            for py_file in python_files:
                with open(os.path.join(submission_path, py_file), 'r') as f:
                    content = f.read()
                    if 'rclpy' in content and 'Node' in content:
                        score += 25.0  # Good sign of ROS 2 usage
                    if 'create_publisher' in content or 'create_subscription' in content:
                        score += 25.0  # Publisher/subscriber detected

            # Cap score at 100
            score = min(score, 100.0)

            return ValidationResult("pass", "ROS 2 package validated successfully", score)

        except Exception as e:
            return ValidationResult("error", f"Validation error: {str(e)}", 0.0)


class SimulationValidator(BaseValidator):
    """Validator for simulation-related exercises"""
    def __init__(self):
        super().__init__("Simulation Validator", "Validates simulation environment and models")

    def validate(self, submission_path: str) -> ValidationResult:
        """Validate a simulation environment submission"""
        try:
            # Check for world files
            world_files = [f for f in os.listdir(submission_path) if f.endswith(('.world', '.sdf', '.urdf'))]

            if not world_files:
                # Check in subdirectories
                for root, dirs, files in os.walk(submission_path):
                    for file in files:
                        if file.endswith(('.world', '.sdf', '.urdf')):
                            world_files.append(os.path.join(root, file))

            if not world_files:
                return ValidationResult("fail", "No simulation world/model files found", 0.0)

            # Check for model directories
            model_dirs = []
            for item in os.listdir(submission_path):
                item_path = os.path.join(submission_path, item)
                if os.path.isdir(item_path):
                    # Check if it looks like a model directory
                    if any(f in os.listdir(item_path) for f in ['model.sdf', 'model.urdf', 'meshes', 'materials']):
                        model_dirs.append(item_path)

            score = 30.0  # Base score for having world files

            if model_dirs:
                score += 40.0  # Bonus for having models

            # Check for config files
            config_files = [f for f in os.listdir(submission_path) if f.endswith(('.yaml', '.config', '.ini'))]
            if config_files:
                score += 30.0  # Bonus for configuration

            score = min(score, 100.0)

            return ValidationResult("pass", f"Simulation validated with {len(world_files)} world files and {len(model_dirs)} models", score)

        except Exception as e:
            return ValidationResult("error", f"Validation error: {str(e)}", 0.0)


class IsaacValidator(BaseValidator):
    """Validator for Isaac-related exercises"""
    def __init__(self):
        super().__init__("Isaac Validator", "Validates Isaac Sim integration and components")

    def validate(self, submission_path: str) -> ValidationResult:
        """Validate an Isaac Sim submission"""
        try:
            # Look for Isaac-specific files
            config_files = []
            py_files = []

            for root, dirs, files in os.walk(submission_path):
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))
                    elif file.endswith(('.yaml', '.json')) and ('isaac' in file.lower() or 'config' in file.lower()):
                        config_files.append(os.path.join(root, file))

            score = 0.0

            # Check for Isaac-specific imports in Python files
            isaac_imports_found = False
            for py_file in py_files:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'omni.' in content or 'isaacsim' in content.lower() or 'carb.' in content:
                        isaac_imports_found = True
                        score += 40.0
                        break

            # Check for config files
            if config_files:
                score += 30.0

            # Check for specific Isaac patterns
            for py_file in py_files:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'SimulationApp' in content:
                        score += 15.0
                    if 'World' in content and 'isaacsim' in content.lower():
                        score += 15.0

            if not isaac_imports_found:
                return ValidationResult("fail", "No Isaac Sim imports found in Python files", 0.0)

            score = min(score, 100.0)

            return ValidationResult("pass", f"Isaac integration validated with {len(config_files)} config files", score)

        except Exception as e:
            return ValidationResult("error", f"Validation error: {str(e)}", 0.0)


class VoiceControlValidator(BaseValidator):
    """Validator for voice control-related exercises"""
    def __init__(self):
        super().__init__("Voice Control Validator", "Validates voice recognition and NLP components")

    def validate(self, submission_path: str) -> ValidationResult:
        """Validate a voice control system submission"""
        try:
            py_files = [f for f in os.listdir(submission_path) if f.endswith('.py')]

            if not py_files:
                # Check subdirectories
                for root, dirs, files in os.walk(submission_path):
                    for file in files:
                        if file.endswith('.py'):
                            py_files.append(os.path.join(root, file))

            score = 0.0
            has_speech_recognition = False
            has_nlp = False
            has_action_mapping = False

            for py_file in py_files:
                with open(py_file, 'r') as f:
                    content = f.read()

                    # Check for speech recognition libraries
                    if any(lib in content for lib in ['speech_recognition', 'pyaudio', 'vosk', 'whisper']):
                        has_speech_recognition = True
                        score += 25.0

                    # Check for NLP libraries or patterns
                    if any(nlp_pattern in content for nlp_pattern in ['nltk', 'spacy', 'transformers', 'intent', 'entity', 'natural language']):
                        has_nlp = True
                        score += 25.0

                    # Check for action/command mapping
                    if any(action_pattern in content for action_pattern in ['action', 'command', 'execute', 'robot', 'move', 'navigate']):
                        has_action_mapping = True
                        score += 25.0

            # Bonus for integration
            if has_speech_recognition and has_nlp and has_action_mapping:
                score += 25.0

            if not (has_speech_recognition or has_nlp or has_action_mapping):
                return ValidationResult("fail", "No voice control components detected", 0.0)

            score = min(score, 100.0)

            return ValidationResult(
                "pass",
                f"Voice control validated: SR={has_speech_recognition}, NLP={has_nlp}, Actions={has_action_mapping}",
                score
            )

        except Exception as e:
            return ValidationResult("error", f"Validation error: {str(e)}", 0.0)


class ValidationFramework:
    """Main validation framework that orchestrates all validators"""
    def __init__(self):
        self.validators = {
            'ros2': ROS2Validator(),
            'simulation': SimulationValidator(),
            'isaac': IsaacValidator(),
            'voice_control': VoiceControlValidator()
        }

    def validate(self, submission_path: str, module_type: str) -> ValidationResult:
        """Validate a submission using the appropriate validator"""
        if module_type not in self.validators:
            return ValidationResult("error", f"Unknown module type: {module_type}", 0.0)

        validator = self.validators[module_type]
        return validator.validate(submission_path)

    def validate_all(self, submission_path: str) -> Dict[str, ValidationResult]:
        """Validate a submission with all available validators"""
        results = {}
        for module_type, validator in self.validators.items():
            results[module_type] = validator.validate(submission_path)
        return results

    def generate_report(self, results: Dict[str, ValidationResult], submission_id: str = None) -> Dict[str, Any]:
        """Generate a comprehensive validation report"""
        overall_score = sum(result.score for result in results.values()) / len(results) if results else 0.0
        passed_validators = sum(1 for result in results.values() if result.status == 'pass')

        report = {
            "submission_id": submission_id or f"sub_{int(time.time())}",
            "timestamp": time.time(),
            "overall_score": round(overall_score, 2),
            "passed_validators": passed_validators,
            "total_validators": len(results),
            "status": "pass" if passed_validators == len(results) else "partial" if passed_validators > 0 else "fail",
            "results": {module: result.to_dict() for module, result in results.items()},
            "summary": {
                "passed": [module for module, result in results.items() if result.status == 'pass'],
                "failed": [module for module, result in results.items() if result.status == 'fail'],
                "errors": [module for module, result in results.items() if result.status == 'error']
            }
        }

        return report


def main():
    """Command-line interface for the validation framework"""
    import argparse

    parser = argparse.ArgumentParser(description='Validation framework for Physical AI & Humanoid Robotics course')
    parser.add_argument('--path', required=True, help='Path to submission to validate')
    parser.add_argument('--module', required=True, choices=['ros2', 'simulation', 'isaac', 'voice_control'],
                       help='Module type to validate against')
    parser.add_argument('--all', action='store_true', help='Run all validators')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--output', help='Output file for results (JSON)')

    args = parser.parse_args()

    framework = ValidationFramework()

    if args.all:
        results = framework.validate_all(args.path)
        report = framework.generate_report(results)
    else:
        result = framework.validate(args.path, args.module)
        results = {args.module: result}
        report = framework.generate_report(results)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(report, indent=2))

    # Exit with error code if validation failed
    if report['status'] == 'fail':
        sys.exit(1)


if __name__ == "__main__":
    main()