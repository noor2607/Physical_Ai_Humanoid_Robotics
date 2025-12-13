import { Router, Request, Response } from 'express';
import { StudentProgress } from '../../models/course';

const router = Router();

// Mock data for demonstration
const mockStudentProgress: StudentProgress[] = [
  {
    student_id: 'student-1',
    module_id: 'module-1-ros2',
    completion_percentage: 0.5,
    last_accessed: new Date(),
    lab_exercises_completed: ['exercise-1'],
    assessments_completed: [],
    notes: 'Making good progress on ROS 2 fundamentals'
  }
];

// GET /students/:studentId/progress - Get student progress
router.get('/:studentId/progress', (req: Request, res: Response) => {
  const studentId = req.params.studentId;
  const studentProgress = mockStudentProgress.filter(sp => sp.student_id === studentId);

  if (studentProgress.length === 0) {
    res.status(404).json({ error: 'Student not found' });
    return;
  }

  res.json({
    studentId: studentId,
    modules_progress: studentProgress,
    lab_exercises_completed: studentProgress.flatMap(sp => sp.lab_exercises_completed),
    assessments_completed: studentProgress.flatMap(sp => sp.assessments_completed),
    overall_completion: studentProgress.reduce((sum, sp) => sum + sp.completion_percentage, 0) / studentProgress.length
  });
});

export default router;