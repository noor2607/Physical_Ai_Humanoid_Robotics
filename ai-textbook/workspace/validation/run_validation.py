#!/usr/bin/env python3
"""
Main validation runner for the Physical AI & Humanoid Robotics course
"""
import argparse
import json
import sys
import os
from pathlib import Path
import yaml
from datetime import datetime

# Add the validation framework to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'framework'))

from validation_framework import ValidationFramework, ValidationResult


def load_config(config_path=None):
    """Load validation configuration"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'validation_config.yaml')

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Return default configuration
        return {
            'validation': {
                'timeout': 60,
                'memory_limit': 2048,
                'cpu_limit': 80,
                'max_file_size': 50
            },
            'modules': {
                'ros2': {'name': 'ROS 2 Fundamentals', 'weight': 25},
                'simulation': {'name': 'Simulation Environments', 'weight': 25},
                'isaac': {'name': 'AI Integration with Isaac', 'weight': 25},
                'voice_control': {'name': 'Voice-Controlled Robotics', 'weight': 25}
            }
        }


def validate_submission(submission_path, module_type, config=None):
    """Validate a single submission"""
    if config is None:
        config = load_config()

    framework = ValidationFramework()
    result = framework.validate(submission_path, module_type)

    return result


def validate_batch(submission_dir, module_type, output_dir=None, config=None):
    """Validate multiple submissions in a directory"""
    if config is None:
        config = load_config()

    framework = ValidationFramework()

    results = {}
    submission_dir_path = Path(submission_dir)

    if not submission_dir_path.exists():
        print(f"Error: Submission directory does not exist: {submission_dir}")
        return results

    # Find all student submission directories
    for student_dir in submission_dir_path.iterdir():
        if student_dir.is_dir():
            print(f"Validating submission for: {student_dir.name}")
            result = framework.validate(str(student_dir), module_type)
            results[student_dir.name] = result.to_dict()

    # Save results if output directory is specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = output_path / f"validation_results_{module_type}_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Batch validation results saved to: {results_file}")

    return results


def generate_html_report(results, output_file):
    """Generate an HTML report from validation results"""
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Validation Report - Physical AI & Humanoid Robotics</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .result { margin: 10px 0; padding: 10px; border-left: 5px solid #ccc; }
        .pass { border-left-color: #4CAF50; background-color: #f9f9f9; }
        .fail { border-left-color: #f44336; background-color: #f9f9f9; }
        .error { border-left-color: #ff9800; background-color: #f9f9f9; }
        .score { font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Validation Report</h1>
        <p>Generated on: {timestamp}</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total submissions: {total_submissions}</p>
        <p>Passed: {passed_count}</p>
        <p>Failed: {failed_count}</p>
        <p>Average score: {average_score:.2f}</p>
    </div>

    <div class="results">
        <h2>Detailed Results</h2>
        {results_html}
    </div>
</body>
</html>
    """

    total_submissions = len(results)
    passed_count = sum(1 for r in results.values() if r.get('status') == 'pass')
    failed_count = total_submissions - passed_count
    average_score = sum(r.get('score', 0) for r in results.values()) / total_submissions if total_submissions > 0 else 0

    results_html = ""
    for student, result in results.items():
        status_class = result.get('status', 'error')
        score = result.get('score', 0)
        message = result.get('message', 'No message')
        details = result.get('details', {})

        result_html = f"""
        <div class="result {status_class}">
            <h3>{student}</h3>
            <p class="score">Score: {score:.2f} | Status: {status_class.upper()}</p>
            <p><strong>Message:</strong> {message}</p>
        """

        if details:
            result_html += "<p><strong>Details:</strong></p><ul>"
            for key, value in details.items():
                result_html += f"<li>{key}: {value}</li>"
            result_html += "</ul>"

        result_html += "</div>"
        results_html += result_html

    html_content = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_submissions=total_submissions,
        passed_count=passed_count,
        failed_count=failed_count,
        average_score=average_score,
        results_html=results_html
    )

    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"HTML report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Run validation for Physical AI & Humanoid Robotics course submissions'
    )

    parser.add_argument(
        'path',
        help='Path to submission (file or directory for batch processing)'
    )

    parser.add_argument(
        '--module',
        choices=['ros2', 'simulation', 'isaac', 'voice_control'],
        help='Module type to validate against (required for single submission)'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process all submissions in the directory'
    )

    parser.add_argument(
        '--config',
        help='Path to validation configuration file'
    )

    parser.add_argument(
        '--html-report',
        help='Generate HTML report to specified file'
    )

    parser.add_argument(
        '--output-dir',
        help='Directory to save validation results (for batch processing)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation output'
    )

    args = parser.parse_args()

    config = load_config(args.config)

    if args.batch:
        # Batch processing mode
        results = validate_batch(args.path, args.module, args.output_dir, config)

        if args.html_report:
            generate_html_report(results, args.html_report)

        if args.verbose:
            print(f"Batch validation completed for {len(results)} submissions")
            for student, result in results.items():
                print(f"  {student}: {result.get('status')} - Score: {result.get('score', 0):.2f}")
    else:
        # Single submission mode
        if not args.module:
            print("Error: --module is required for single submission validation")
            sys.exit(1)

        result = validate_submission(args.path, args.module, config)

        if args.verbose:
            print(f"Validation Result:")
            print(f"  Status: {result.status}")
            print(f"  Score: {result.score}")
            print(f"  Message: {result.message}")
            if result.details:
                print(f"  Details: {result.details}")

        # Output result as JSON
        print(json.dumps(result.to_dict(), indent=2))

        # Set exit code based on result
        if result.status == 'fail':
            sys.exit(1)
        elif result.status == 'error':
            sys.exit(2)


if __name__ == "__main__":
    main()