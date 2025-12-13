import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';

// Import routes
import modulesRouter from './routes/modules';
import chaptersRouter from './routes/chapters';
import exercisesRouter from './routes/exercises';
import studentsRouter from './routes/students';
import usersRouter from './routes/users';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS for all routes
app.use(morgan('combined')); // HTTP request logging
app.use(express.json({ limit: '10mb' })); // Parse JSON request bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded request bodies

// API Routes
app.use('/api/v1/modules', modulesRouter);
app.use('/api/v1/chapters', chaptersRouter);
app.use('/api/v1/exercises', exercisesRouter);
app.use('/api/v1/students', studentsRouter);
app.use('/api/v1/users', usersRouter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Physical AI & Humanoid Robotics Course API',
    version: '1.0.0',
    endpoints: [
      { method: 'GET', path: '/api/v1/modules', description: 'List all course modules' },
      { method: 'GET', path: '/api/v1/modules/:id', description: 'Get module details' },
      { method: 'GET', path: '/api/v1/chapters', description: 'List all chapters' },
      { method: 'GET', path: '/api/v1/chapters/:id', description: 'Get chapter details' },
      { method: 'GET', path: '/api/v1/exercises', description: 'List all lab exercises' },
      { method: 'POST', path: '/api/v1/exercises/:id/validate', description: 'Validate exercise completion' },
      { method: 'GET', path: '/api/v1/students/:id/progress', description: 'Get student progress' }
    ]
  });
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler for undefined routes
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Physical AI & Humanoid Robotics Course API server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`API Documentation: http://localhost:${PORT}/`);
});

export default app;