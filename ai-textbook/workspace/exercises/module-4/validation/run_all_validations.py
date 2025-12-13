#!/usr/bin/env python3
"""
Main validation runner for Module 4 Lab Exercises
This script runs all validation scripts for Module 4 lab exercises.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_validation_script(script_path):
    """Run a single validation script and return the result."""
    print(f"Running validation: {script_path}")

    try:
        result = subprocess.run([sys.executable, script_path],
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Validation script timed out: {script_path}")
        return False
    except Exception as e:
        print(f"Error running validation script {script_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Module 4 Lab Exercise Validation Runner')
    parser.add_argument('--lab', type=int, choices=range(1, 6),
                       help='Run validation for a specific lab exercise (1-5)')
    parser.add_argument('--all', action='store_true',
                       help='Run validation for all lab exercises')

    args = parser.parse_args()

    # Get the directory of this script
    script_dir = Path(__file__).parent
    validation_dir = script_dir

    print("Module 4 Lab Exercise Validation Runner")
    print("=" * 50)

    if args.lab:
        # Run validation for a specific lab
        script_name = f"validate_lab{args.lab}_*.py"
        script_path = None

        for file in validation_dir.glob(script_name):
            script_path = file
            break

        if script_path:
            success = run_validation_script(script_path)
            print(f"\nLab {args.lab} Validation: {'PASS' if success else 'FAIL'}")
            return 0 if success else 1
        else:
            print(f"Validation script not found for Lab {args.lab}")
            return 1

    elif args.all or not (args.lab or args.all):
        # Run validation for all labs
        all_success = True

        for lab_num in range(1, 6):
            script_name = f"validate_lab{lab_num}_*.py"
            script_path = None

            for file in validation_dir.glob(script_name):
                script_path = file
                break

            if script_path:
                success = run_validation_script(script_path)
                print(f"\nLab {lab_num} Validation: {'PASS' if success else 'FAIL'}")
                print("-" * 30)

                if not success:
                    all_success = False
            else:
                print(f"Validation script not found for Lab {lab_num}")
                all_success = False

        print(f"\nOverall Validation: {'PASS' if all_success else 'FAIL'}")
        return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())