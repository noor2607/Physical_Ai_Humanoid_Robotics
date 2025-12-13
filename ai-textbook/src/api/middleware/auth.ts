import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// In a real application, this would come from environment variables
const JWT_SECRET = process.env.JWT_SECRET || 'physical_ai_course_secret_key';

// Mock user database (in reality, this would be connected to a real database)
const mockUsers = [
  {
    id: '1',
    username: 'student1',
    email: 'student1@physical-ai-course.com',
    password: 'hashed_password_here', // In reality, this would be a hashed password
    role: 'student'
  },
  {
    id: '2',
    username: 'instructor1',
    email: 'instructor1@physical-ai-course.com',
    password: 'hashed_password_here',
    role: 'instructor'
  }
];

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    username: string;
    email: string;
    role: string;
  };
}

// Generate JWT token
export const generateToken = (user: any): string => {
  return jwt.sign(
    {
      id: user.id,
      username: user.username,
      email: user.email,
      role: user.role
    },
    JWT_SECRET,
    { expiresIn: '24h' }
  );
};

// Middleware to authenticate token
export const authenticateToken = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, decoded: any) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }

    // Find user in mock database
    const user = mockUsers.find(u => u.id === decoded.id);
    if (!user) {
      return res.status(403).json({ error: 'User no longer exists' });
    }

    req.user = user;
    next();
  });
};

// Middleware to check user role
export const requireRole = (roles: string[]) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

// Check if user is authenticated
export const isAuthenticated = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  if (!req.headers['authorization']) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  next();
};