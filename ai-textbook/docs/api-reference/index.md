---
sidebar_position: 1
title: "API Reference"
---

# API Reference

This section documents the API endpoints available for the Physical AI & Humanoid Robotics course. These endpoints enable progress tracking, exercise validation, and assessment functionality.

## Module 1 API Endpoints

The following endpoints are available for Module 1 (ROS 2 Fundamentals):

### GET /api/v1/module1/progress

Retrieve progress information for Module 1.

**Parameters**:
- `student_id` (required): Unique identifier for the student

**Response**:
```json
{
  "student_id": "string",
  "module_id": "module-1-ros2",
  "module_name": "ROS 2 Fundamentals",
  "completion_percentage": 0.0,
  "completed_chapters": [],
  "completed_exercises": [],
  "assessment_score": null,
  "last_accessed": "ISO timestamp"
}
```

### POST /api/v1/module1/exercise/submit

Submit an exercise for validation and store the results.

**Request Body**:
```json
{
  "exercise_id": "string",
  "student_id": "string",
  "solution": "string"
}
```

**Response**:
```json
{
  "exercise_id": "string",
  "student_id": "string",
  "passed": true,
  "feedback": "string",
  "timestamp": "ISO timestamp"
}
```

### POST /api/v1/module1/exercise/validate

Validate an exercise solution without storing it.

**Request Body**:
```json
{
  "exercise_id": "string",
  "solution": "string"
}
```

**Response**:
```json
{
  "exercise_id": "string",
  "passed": true,
  "feedback": "string",
  "details": ["array", "of", "validation", "details"],
  "timestamp": "ISO timestamp"
}
```

### GET /api/v1/module1/status

Get status information for Module 1 implementation.

**Response**:
```json
{
  "module": "Module 1: ROS 2 Fundamentals",
  "status": "implemented",
  "chapters_available": 5,
  "exercises_available": 5,
  "api_endpoints": [
    "/api/v1/module1/progress",
    "/api/v1/module1/exercise/submit",
    "/api/v1/module1/exercise/validate"
  ],
  "last_updated": "ISO timestamp"
}
```

## Module 4 API Endpoints

The following endpoints are available for Module 4 (Voice-Controlled Robotics):

### GET /api/v1/module4/progress

Retrieve progress information for Module 4.

**Parameters**:
- `student_id` (required): Unique identifier for the student

**Response**:
```json
{
  "student_id": "string",
  "module_id": "module-4-vla",
  "module_name": "Voice-Controlled Robotics",
  "completion_percentage": 0.0,
  "completed_chapters": [],
  "completed_exercises": [],
  "completed_labs": [],
  "assessment_score": null,
  "capstone_progress": {
    "phase": "not_started",
    "milestones_completed": [],
    "last_updated": null
  },
  "last_accessed": "ISO timestamp"
}
```

### POST /api/v1/module4/lab/submit

Submit a lab exercise for validation and store the results.

**Request Body**:
```json
{
  "lab_id": "string",
  "student_id": "string",
  "solution": "string"
}
```

**Response**:
```json
{
  "lab_id": "string",
  "student_id": "string",
  "passed": true,
  "feedback": "string",
  "timestamp": "ISO timestamp"
}
```

### POST /api/v1/module4/lab/validate

Validate a lab solution without storing it.

**Request Body**:
```json
{
  "lab_id": "string",
  "solution": "string"
}
```

**Response**:
```json
{
  "lab_id": "string",
  "passed": true,
  "feedback": "string",
  "details": [
    "array",
    "of",
    "validation",
    "details"
  ],
  "timestamp": "ISO timestamp"
}
```

### POST /api/v1/module4/capstone/progress

Update capstone project progress for a student.

**Request Body**:
```json
{
  "student_id": "string",
  "phase": "string",
  "milestones_completed": ["array", "of", "milestone", "names"],
  "notes": "string"
}
```

**Response**:
```json
{
  "student_id": "string",
  "phase": "string",
  "milestones_completed": ["array", "of", "milestone", "names"],
  "notes": "string",
  "updated_at": "ISO timestamp"
}
```

### POST /api/v1/module4/capstone/submit

Submit capstone project for evaluation.

**Request Body**:
```json
{
  "student_id": "string",
  "project_files": "string or object containing project files",
  "evaluation_criteria": ["array", "of", "criteria"]
}
```

**Response**:
```json
{
  "student_id": "string",
  "project_submitted": true,
  "evaluation_status": "pending",
  "evaluation_criteria_met": ["array", "of", "criteria"],
  "overall_score": 0.0,
  "feedback_summary": "string",
  "detailed_feedback": ["array", "of", "detailed", "feedback"],
  "timestamp": "ISO timestamp"
}
```

### GET /api/v1/module4/capstone/status

Get status information for the capstone project.

**Parameters**:
- `student_id` (required): Unique identifier for the student

**Response**:
```json
{
  "student_id": "string",
  "capstone_project": "Autonomous Humanoid Final Project",
  "status": "not_started",
  "phase": "string",
  "milestones_completed": ["array", "of", "completed", "milestones"],
  "remaining_milestones": ["array", "of", "remaining", "milestones"],
  "estimated_completion": "ISO date string",
  "last_updated": "ISO timestamp"
}
```

### GET /api/v1/module4/status

Get status information for Module 4 implementation.

**Response**:
```json
{
  "module": "Module 4: Voice-Controlled Robotics",
  "status": "implemented",
  "chapters_available": 4,
  "labs_available": 5,
  "capstone_project": "Autonomous Humanoid Final Project",
  "api_endpoints": [
    "/api/v1/module4/progress",
    "/api/v1/module4/lab/submit",
    "/api/v1/module4/lab/validate",
    "/api/v1/module4/capstone/progress",
    "/api/v1/module4/capstone/submit",
    "/api/v1/module4/capstone/status"
  ],
  "last_updated": "ISO timestamp"
}
```

## Implementation

The API endpoints are implemented in:
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/api/module1_endpoints.py`
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/api/module4_endpoints.py`

This Flask-based API provides the backend functionality for tracking student progress and validating exercise submissions automatically.