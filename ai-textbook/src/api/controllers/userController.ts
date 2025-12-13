import { Request, Response } from 'express';
import { generateToken } from '../middleware/auth';
import { Student } from '../models/course';

// Mock database for users (in a real application, this would connect to a real database)
const mockStudents: Student[] = [
  {
    id: 'student-1',
    name: 'John Doe',
    enrollment_date: new Date('2025-01-15'),
    progress: [],
    completed_modules: [],
    assessment_results: []
  }
];

// Register a new user
export const register = async (req: Request, res: Response) => {
  try {
    const { username, email, password } = req.body;

    // In a real application, you would:
    // 1. Validate input
    // 2. Hash the password
    // 3. Save user to database
    // 4. Create student profile

    // For this example, we'll return a mock response
    const newUser = {
      id: `user-${Date.now()}`,
      username,
      email,
      role: 'student'
    };

    const token = generateToken(newUser);

    res.status(201).json({
      message: 'User registered successfully',
      token,
      user: newUser
    });
  } catch (error) {
    res.status(500).json({ error: 'Registration failed' });
  }
};

// Login user
export const login = async (req: Request, res: Response) => {
  try {
    const { username, password } = req.body;

    // In a real application, you would:
    // 1. Validate input
    // 2. Find user in database
    // 3. Compare password hash
    // 4. Generate JWT token

    // For this example, we'll mock a successful login
    const user = {
      id: 'user-1',
      username: username,
      email: `${username}@physical-ai-course.com`,
      role: 'student'
    };

    const token = generateToken(user);

    res.json({
      message: 'Login successful',
      token,
      user
    });
  } catch (error) {
    res.status(500).json({ error: 'Login failed' });
  }
};

// Get current user profile
export const getProfile = async (req: any, res: Response) => {
  try {
    // The user is attached to the request by the authentication middleware
    const user = req.user;

    if (!user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    res.json({
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get user profile' });
  }
};

// Update user profile
export const updateProfile = async (req: any, res: Response) => {
  try {
    const user = req.user;
    const updates = req.body;

    if (!user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    // In a real application, you would update the user in the database
    // For this example, we'll return a mock response
    res.json({
      message: 'Profile updated successfully',
      updatedUser: { ...user, ...updates }
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update profile' });
  }
};

// Get all students (for instructors)
export const getAllStudents = async (req: any, res: Response) => {
  try {
    // In a real application, you would fetch from the database
    // Only return necessary information
    const students = mockStudents.map(student => ({
      id: student.id,
      name: student.name,
      enrollment_date: student.enrollment_date
    }));

    res.json({
      students,
      count: students.length
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch students' });
  }
};