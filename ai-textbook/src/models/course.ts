// Course-related entities for Physical AI & Humanoid Robotics Course

export interface CourseModule {
  id: string;
  name: string;
  description: string;
  duration: number; // in weeks
  learning_objectives: string[];
  chapters: string[]; // IDs of chapters in this module
  prerequisites: string[];
  assessments: string[]; // IDs of assessments associated with this module
}

export interface Chapter {
  id: string;
  title: string;
  module_id: string; // Reference to the parent module
  content: string;
  learning_objectives: string[];
  activities: string[];
  code_examples: string[]; // IDs of code examples in the chapter
  lab_exercises: string[]; // IDs of lab exercises associated with the chapter
}

export interface Student {
  id: string;
  name: string;
  enrollment_date: Date;
  progress: StudentProgress[];
  completed_modules: string[]; // IDs of completed modules
  assessment_results: AssessmentResult[]; // Results of assessments
}

export interface LabExercise {
  id: string;
  title: string;
  module_id: string; // Reference to the parent module
  chapter_id: string; // Reference to the parent chapter
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_time: number; // in minutes
  requirements: string[];
  instructions: string;
  solution: string;
  validation_criteria: string[];
}

export interface Assessment {
  id: string;
  module_id: string; // Reference to the parent module
  title: string;
  type: 'quiz' | 'project' | 'capstone';
  requirements: string[];
  evaluation_criteria: string[];
  rubric: AssessmentRubric;
}

export interface AssessmentResult {
  student_id: string; // Reference to the student
  assessment_id: string; // Reference to the assessment
  score: number; // Score received (0.0 to 1.0 scale)
  feedback: string;
  submission_date: Date;
  evaluation_date: Date;
}

export interface CodeExample {
  id: string;
  chapter_id: string; // Reference to the parent chapter
  title: string;
  language: string; // Programming language (Python, C++, etc.)
  code: string;
  description: string;
  use_case: string;
  dependencies: string[];
}

export interface RobotSystem {
  id: string;
  name: string; // Name of the robot (e.g., "Unitree Go1", "NAO Robot")
  type: 'humanoid' | 'wheeled' | 'manipulator' | 'other';
  simulation_environment: 'Gazebo' | 'Unity' | 'Isaac Sim';
  sensors: string[];
  actuators: string[];
  capabilities: string[];
  configuration: RobotConfiguration;
}

export interface StudentProgress {
  student_id: string; // Reference to the student
  module_id: string; // Reference to the module
  completion_percentage: number; // Percentage of module completed (0.0 to 1.0)
  last_accessed: Date;
  lab_exercises_completed: string[]; // IDs of completed lab exercises
  assessments_completed: string[]; // IDs of completed assessments
  notes: string;
}

export interface AssessmentRubric {
  criteria: RubricCriteria[];
  total_points: number;
}

export interface RubricCriteria {
  name: string;
  description: string;
  points: number;
}

export interface RobotConfiguration {
  hardware: HardwareSpecs;
  software: SoftwareSpecs;
}

export interface HardwareSpecs {
  processor: string;
  memory: string;
  storage: string;
  sensors: string[];
  actuators: string[];
}

export interface SoftwareSpecs {
  os: string;
  ros_version: string;
  simulation_env: string;
  additional_packages: string[];
}