import { Router } from 'express';
import { register, login, getProfile, updateProfile, getAllStudents } from '../controllers/userController';
import { authenticateToken, requireRole, isAuthenticated } from '../middleware/auth';

const router = Router();

// Public routes
router.post('/register', register);
router.post('/login', login);

// Protected routes - require authentication
router.get('/profile', authenticateToken, getProfile);
router.put('/profile', authenticateToken, updateProfile);

// Instructor-only routes
router.get('/students', authenticateToken, requireRole(['instructor', 'admin']), getAllStudents);

export default router;