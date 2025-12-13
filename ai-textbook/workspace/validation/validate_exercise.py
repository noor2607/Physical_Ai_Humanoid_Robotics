#!/usr/bin/env python3
"""
Command-line interface for validating exercises in the Physical AI & Humanoid Robotics course
"""
import argparse
import json
import sys
import os
from pathlib import Path

# Add the validation framework to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'framework'))

from validation_framework import ValidationFramework, ValidationResult


def validate_exercise(submission_path, module_type, verbose=False, report=False):
    """
    Validate a specific exercise submission
    """
    framework = ValidationFramework()

    if not os.path.exists(submission_path):
        print(f"Error: Submission path does not exist: {submission_path}")
        return None

    if not os.path.isdir(submission_path):
        print(f"Error: Submission path is not a directory: {submission_path}")
        return None

    # Validate the submission
    result = framework.validate(submission_path, module_type)

    if verbose:
        print(f"Validation Result for {module_type}:")
        print(f"  Status: {result.status}")
        print(f"  Score: {result.score}")
        print(f"  Message: {result.message}")
        if result.details:
            print(f"  Details: {result.details}")

    # Generate report if requested
    if report:
        all_results = framework.validate_all(submission_path)
        report_data = framework.generate_report(all_results)

        if verbose:
            print("\nDetailed Report:")
            print(json.dumps(report_data, indent=2))

        return report_data
    else:
        return result.to_dict()


def validate_project(submission_path, module_type, verbose=False):
    """
    Validate a project submission (more comprehensive than exercises)
    """
    framework = ValidationFramework()

    if not os.path.exists(submission_path):
        print(f"Error: Submission path does not exist: {submission_path}")
        return None

    # For projects, run all validators to check integration
    all_results = framework.validate_all(submission_path)
    report_data = framework.generate_report(all_results)

    if verbose:
        print(f"Project Validation Report for {module_type}:")
        print(json.dumps(report_data, indent=2))

    return report_data


def validate_all_modules(submission_path, verbose=False):
    """
    Validate a submission against all available modules
    """
    framework = ValidationFramework()

    if not os.path.exists(submission_path):
        print(f"Error: Submission path does not exist: {submission_path}")
        return None

    all_results = framework.validate_all(submission_path)
    report_data = framework.generate_report(all_results)

    if verbose:
        print("Validation Report for All Modules:")
        print(json.dumps(report_data, indent=2))

    return report_data


def main():
    parser = argparse.ArgumentParser(
        description='Validate exercises and projects for the Physical AI & Humanoid Robotics course'
    )

    parser.add_argument(
        'path',
        help='Path to the submission to validate'
    )

    parser.add_argument(
        '--module',
        choices=['ros2', 'simulation', 'isaac', 'voice_control'],
        required=True,
        help='Module type to validate against'
    )

    parser.add_argument(
        '--project',
        action='store_true',
        help='Validate as a project (more comprehensive)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate against all modules'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation output'
    )

    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed report'
    )

    parser.add_argument(
        '--output',
        help='Output file for validation results (JSON format)'
    )

    args = parser.parse_args()

    # Perform validation based on arguments
    if args.all:
        result = validate_all_modules(args.path, args.verbose)
    elif args.project:
        result = validate_project(args.path, args.module, args.verbose)
    else:
        result = validate_exercise(args.path, args.module, args.verbose, args.report)

    if result is None:
        sys.exit(1)  # Error occurred

    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        if args.verbose:
            print(f"Results written to {args.output}")
    else:
        print(json.dumps(result, indent=2))

    # Determine exit code based on validation status
    if isinstance(result, dict):
        status = result.get('status', 'error')
        if status == 'fail':
            sys.exit(1)
        elif status == 'error':
            sys.exit(2)
    elif hasattr(result, 'status'):
        if result.status == 'fail':
            sys.exit(1)

    if args.verbose:
        print("Validation completed successfully!")


if __name__ == "__main__":
    main()