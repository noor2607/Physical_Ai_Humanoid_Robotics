import { Router, Request, Response } from 'express';
import { CourseModule } from '../../models/course';

const router = Router();

// Mock data for demonstration
const mockModules: CourseModule[] = [
  {
    id: 'module-1-ros2',
    name: 'Robotic Nervous System (ROS 2)',
    description: 'Understanding the ROS 2 architecture, nodes, and communication patterns',
    duration: 3,
    learning_objectives: [
      'Understand ROS 2 architecture',
      'Install and configure ROS 2',
      'Create basic publisher/subscriber nodes'
    ],
    chapters: ['chapter-1', 'chapter-2', 'chapter-3', 'chapter-4', 'chapter-5'],
    prerequisites: [],
    assessments: ['assessment-1']
  },
  {
    id: 'module-2-simulation',
    name: 'Digital Twin (Gazebo & Unity)',
    description: 'Physics simulation, sensor simulation, environment setup, and Unity visualization',
    duration: 3,
    learning_objectives: [
      'Understand Gazebo physics engine',
      'Create simulation environments',
      'Implement Unity visualization'
    ],
    chapters: ['chapter-6', 'chapter-7', 'chapter-8', 'chapter-9'],
    prerequisites: ['module-1-ros2'],
    assessments: ['assessment-2']
  }
];

// GET /modules - List all course modules
router.get('/', (req: Request, res: Response) => {
  res.json(mockModules);
});

// GET /modules/:moduleId - Get module details
router.get('/:moduleId', (req: Request, res: Response) => {
  const moduleId = req.params.moduleId;
  const module = mockModules.find(m => m.id === moduleId);

  if (!module) {
    res.status(404).json({ error: 'Module not found' });
    return;
  }

  res.json(module);
});

export default router;