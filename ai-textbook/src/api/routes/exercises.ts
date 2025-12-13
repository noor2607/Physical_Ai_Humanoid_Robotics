import { Router, Request, Response } from 'express';
import { LabExercise } from '../../models/course';

const router = Router();

// Mock data for demonstration
const mockExercises: LabExercise[] = [
  {
    id: 'exercise-1',
    title: 'Basic Publisher/Subscriber',
    module_id: 'module-1-ros2',
    chapter_id: 'chapter-1',
    description: 'Create a basic publisher and subscriber to exchange messages',
    difficulty: 'beginner',
    estimated_time: 45,
    requirements: ['ROS 2 Humble Hawksbill', 'Python 3.8+'],
    instructions: 'Create a publisher node that sends messages and a subscriber node that receives them',
    solution: 'Complete code example for publisher/subscriber',
    validation_criteria: ['Publisher node runs', 'Subscriber receives messages', 'Nodes communicate properly']
  },
  {
    id: 'exercise-2',
    title: 'Service Client/Server',
    module_id: 'module-1-ros2',
    chapter_id: 'chapter-2',
    description: 'Implement a service server and client for request/response communication',
    difficulty: 'intermediate',
    estimated_time: 60,
    requirements: ['ROS 2 Humble Hawksbill', 'Python 3.8+'],
    instructions: 'Create a service server that responds to requests and a client that calls the service',
    solution: 'Complete code example for service client/server',
    validation_criteria: ['Service server runs', 'Client calls service', 'Response received correctly']
  }
];

// GET /exercises - List all lab exercises with filtering options
router.get('/', (req: Request, res: Response) => {
  let filteredExercises = [...mockExercises];

  // Apply filters if provided
  const moduleId = req.query.moduleId as string;
  const chapterId = req.query.chapterId as string;
  const difficulty = req.query.difficulty as string;

  if (moduleId) {
    filteredExercises = filteredExercises.filter(e => e.module_id === moduleId);
  }

  if (chapterId) {
    filteredExercises = filteredExercises.filter(e => e.chapter_id === chapterId);
  }

  if (difficulty) {
    filteredExercises = filteredExercises.filter(e => e.difficulty === difficulty);
  }

  res.json(filteredExercises);
});

// POST /exercises/:exerciseId/validate - Validate exercise completion
router.post('/:exerciseId/validate', (req: Request, res: Response) => {
  const exerciseId = req.params.exerciseId;
  const submission = req.body;

  // Find the exercise to validate
  const exercise = mockExercises.find(e => e.id === exerciseId);

  if (!exercise) {
    res.status(404).json({ error: 'Exercise not found' });
    return;
  }

  // In a real implementation, we would validate the submission
  // For now, we'll return a mock validation result
  const validationResult = {
    exerciseId: exerciseId,
    studentId: submission.studentId || 'unknown',
    passed: true,
    feedback: 'Exercise completed successfully',
    score: 1.0,
    validation_details: ['All validation criteria met']
  };

  res.json(validationResult);
});

export default router;