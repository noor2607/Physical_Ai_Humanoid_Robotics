# Automated Validation Tools

This directory contains the automated validation framework for the Physical AI & Humanoid Robotics course. The tools provide comprehensive validation for exercises and projects across all four modules.

## Overview

The validation framework includes:

- **Module-specific validators** for ROS 2, Simulation, Isaac, and Voice Control
- **Command-line interface** for easy validation
- **Batch processing** for multiple submissions
- **Detailed reporting** with JSON and HTML output
- **Configurable validation rules** through YAML configuration

## Installation and Setup

The validation tools are located in the `framework/` directory and can be used directly from this directory.

## Usage

### Validate a Single Exercise

```bash
python validate_exercise.py /path/to/submission --module ros2
```

### Validate a Project

```bash
python validate_exercise.py /path/to/submission --module voice_control --project
```

### Validate Against All Modules

```bash
python validate_exercise.py /path/to/submission --all
```

### Generate Detailed Report

```bash
python validate_exercise.py /path/to/submission --module simulation --report --verbose
```

### Batch Validation

```bash
python run_validation.py /path/to/submissions --module ros2 --batch --verbose
```

### Generate HTML Report

```bash
python run_validation.py /path/to/submission --module isaac --html-report report.html --verbose
```

## Command-Line Options

### validate_exercise.py

- `path`: Path to the submission to validate
- `--module`: Module type to validate against (ros2, simulation, isaac, voice_control)
- `--project`: Validate as a project (more comprehensive)
- `--all`: Validate against all modules
- `--verbose`: Show detailed validation output
- `--report`: Generate detailed report
- `--output`: Output file for validation results (JSON format)

### run_validation.py

- `path`: Path to submission (file or directory for batch processing)
- `--module`: Module type to validate against
- `--batch`: Process all submissions in the directory
- `--config`: Path to validation configuration file
- `--html-report`: Generate HTML report to specified file
- `--output-dir`: Directory to save validation results (for batch processing)
- `--verbose`: Show detailed validation output

## Validation Modules

### ROS 2 Validator
Validates ROS 2 package structure, build process, and basic functionality.

### Simulation Validator
Validates simulation environments, world files, and robot models.

### Isaac Validator
Validates Isaac Sim integration and AI components.

### Voice Control Validator
Validates speech recognition, NLP, and voice-to-action systems.

## Configuration

The validation behavior can be customized through `validation_config.yaml`. This file allows you to configure:

- Timeouts and resource limits
- Module weights and validation criteria
- Feedback templates
- Security checks

## Output Format

Validation results are returned in JSON format:

```json
{
  "status": "pass",
  "score": 85.5,
  "message": "Validation message",
  "details": {},
  "timestamp": 1234567890.123
}
```

For batch processing, the output includes aggregate statistics and individual results.

## Integration with Course Platform

The validation tools can be integrated with the course platform through API endpoints. See the automated-validation-tools.md documentation for details.

## Troubleshooting

### Common Issues

1. **File not found**: Ensure the submission path is correct and accessible
2. **Permission errors**: Check file permissions for the submission
3. **Timeout errors**: Increase timeout in configuration or optimize code
4. **Dependency issues**: Ensure all required packages are installed

### Debugging

Use the `--verbose` flag to get detailed output during validation:

```bash
python validate_exercise.py /path/to/submission --module ros2 --verbose
```

## Security Considerations

The validation framework includes security checks to prevent malicious code execution. All validation runs in a controlled environment with resource limits.

## Extending the Framework

New validators can be created by extending the `BaseValidator` class and implementing the `validate` method. Custom validators can be added to the main framework.

## Support

For questions about the validation tools, contact the course support team at validation-support@physical-ai-course.com.