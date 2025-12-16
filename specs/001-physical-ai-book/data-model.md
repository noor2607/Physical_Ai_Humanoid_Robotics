# Data Model: Physical AI & Humanoid Robotics Course Book

## Course Module
- **name**: String - The module name (e.g., "ROS 2 Fundamentals", "NVIDIA Isaac Platform")
- **description**: String - Detailed description of the module content
- **duration**: Integer - Number of weeks for the module
- **learning_objectives**: Array<String> - List of learning objectives for the module
- **chapters**: Array<Chapter> - References to chapters in this module
- **prerequisites**: Array<String> - Prerequisites for this module
- **assessments**: Array<Assessment> - Assessments associated with this module

## Chapter
- **title**: String - The chapter title
- **module_id**: String - Reference to the parent module
- **content**: String - Detailed chapter content
- **learning_objectives**: Array<String> - Learning objectives for this chapter
- **activities**: Array<String> - Activities and exercises in the chapter
- **code_examples**: Array<CodeExample> - Code examples in the chapter
- **lab_exercises**: Array<LabExercise> - Lab exercises associated with the chapter

## Student
- **id**: String - Unique identifier for the student
- **name**: String - Student name
- **enrollment_date**: Date - Date when student enrolled in the course
- **progress**: Array<StudentProgress> - Progress tracking for each module
- **completed_modules**: Array<String> - IDs of completed modules
- **assessment_results**: Array<AssessmentResult> - Results of assessments

## Lab Exercise
- **id**: String - Unique identifier for the exercise
- **title**: String - Title of the lab exercise
- **module_id**: String - Reference to the parent module
- **chapter_id**: String - Reference to the parent chapter
- **description**: String - Detailed description of the exercise
- **difficulty**: String - Difficulty level (beginner, intermediate, advanced)
- **estimated_time**: Integer - Estimated completion time in minutes
- **requirements**: Array<String> - Hardware/software requirements
- **instructions**: String - Step-by-step instructions
- **solution**: String - Solution guide
- **validation_criteria**: Array<String> - Criteria for validating completion

## Assessment
- **id**: String - Unique identifier for the assessment
- **module_id**: String - Reference to the parent module
- **title**: String - Title of the assessment
- **type**: String - Type of assessment (quiz, project, capstone)
- **requirements**: Array<String> - Requirements for the assessment
- **evaluation_criteria**: Array<String> - Criteria for evaluation
- **rubric**: AssessmentRubric - Grading rubric for the assessment

## Assessment Result
- **student_id**: String - Reference to the student
- **assessment_id**: String - Reference to the assessment
- **score**: Float - Score received (0.0 to 1.0 scale)
- **feedback**: String - Instructor feedback
- **submission_date**: Date - Date of submission
- **evaluation_date**: Date - Date of evaluation

## Code Example
- **id**: String - Unique identifier for the code example
- **chapter_id**: String - Reference to the parent chapter
- **title**: String - Title of the code example
- **language**: String - Programming language (Python, C++, etc.)
- **code**: String - The actual code content
- **description**: String - Description of what the code does
- **use_case**: String - Use case or scenario where the code applies
- **dependencies**: Array<String> - Dependencies required for the code

## Robot System
- **id**: String - Unique identifier for the robot system
- **name**: String - Name of the robot (e.g., "Unitree Go1", "NAO Robot")
- **type**: String - Type of robot (humanoid, wheeled, manipulator, etc.)
- **simulation_environment**: String - Supported simulation environment (Gazebo, Unity, Isaac Sim)
- **sensors**: Array<String> - List of sensors on the robot
- **actuators**: Array<String> - List of actuators on the robot
- **capabilities**: Array<String> - Capabilities of the robot
- **configuration**: RobotConfiguration - Hardware and software configuration

## Student Progress
- **student_id**: String - Reference to the student
- **module_id**: String - Reference to the module
- **completion_percentage**: Float - Percentage of module completed (0.0 to 1.0)
- **last_accessed**: Date - Date of last access to the module
- **lab_exercises_completed**: Array<String> - IDs of completed lab exercises
- **assessments_completed**: Array<String> - IDs of completed assessments
- **notes**: String - Additional notes about student progress

## Validation Rules
- Course Module: name must be unique within the course, duration must be positive
- Chapter: must belong to exactly one module, title must be unique within module
- Student: id must be unique, name is required
- Lab Exercise: difficulty must be one of ["beginner", "intermediate", "advanced"]
- Assessment: type must be one of ["quiz", "project", "capstone"]
- Code Example: language must be supported by the course (Python, C++)
- Robot System: type must be one of ["humanoid", "wheeled", "manipulator", "other"]
- Assessment Result: score must be between 0.0 and 1.0

## State Transitions
- Student Progress: incomplete → in-progress → completed (based on completion percentage thresholds)
- Assessment: not-started → in-progress → submitted → evaluated
- Lab Exercise: not-started → in-progress → completed → validated