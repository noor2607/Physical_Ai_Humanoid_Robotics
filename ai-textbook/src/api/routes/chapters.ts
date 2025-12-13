import { Router, Request, Response } from 'express';
import { Chapter } from '../../models/course';

const router = Router();

// Mock data for demonstration
const mockChapters: Chapter[] = [
  {
    id: 'chapter-1',
    title: 'ROS 2 Fundamentals',
    module_id: 'module-1-ros2',
    content: 'Understanding the ROS 2 architecture, nodes, and communication patterns',
    learning_objectives: [
      'Understand ROS 2 architecture',
      'Install and configure ROS 2',
      'Create basic publisher/subscriber nodes'
    ],
    activities: ['ROS 2 installation', 'Basic node creation', 'Topic communication'],
    code_examples: ['example-1', 'example-2'],
    lab_exercises: ['exercise-1', 'exercise-2']
  },
  {
    id: 'chapter-2',
    title: 'Nodes, Topics, Services',
    module_id: 'module-1-ros2',
    content: 'Deep dive into ROS 2 communication mechanisms',
    learning_objectives: [
      'Master nodes, topics, services, and actions',
      'Implement parameter servers'
    ],
    activities: ['Advanced communication patterns', 'Service calls', 'Action servers'],
    code_examples: ['example-3', 'example-4'],
    lab_exercises: ['exercise-3', 'exercise-4']
  }
];

// GET /chapters - List all chapters
router.get('/', (req: Request, res: Response) => {
  res.json(mockChapters);
});

// GET /chapters/:chapterId - Get chapter details
router.get('/:chapterId', (req: Request, res: Response) => {
  const chapterId = req.params.chapterId;
  const chapter = mockChapters.find(c => c.id === chapterId);

  if (!chapter) {
    res.status(404).json({ error: 'Chapter not found' });
    return;
  }

  res.json(chapter);
});

export default router;