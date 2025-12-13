---
title: "Progress Tracking and Analytics"
sidebar_label: "Progress Tracking"
sidebar_position: 107
---

# Progress Tracking and Analytics System

## Overview

This document describes the progress tracking and analytics system for the Physical AI & Humanoid Robotics course. The system provides comprehensive tracking of student progress across all modules, detailed analytics for instructors, and personalized learning paths for students.

## System Architecture

### Core Components

#### 1. Data Collection Layer
- **Event Tracking**: Captures student interactions with course materials
- **Assessment Results**: Records scores and performance on exercises
- **Time Tracking**: Monitors time spent on different activities
- **Engagement Metrics**: Tracks participation in discussions and collaborative activities

#### 2. Data Storage Layer
- **Student Profiles**: Individual progress and learning history
- **Module Progress**: Completion status for each module component
- **Assessment History**: Detailed records of all assessments
- **Interaction Logs**: Complete logs of student interactions

#### 3. Analytics Engine
- **Performance Analysis**: Identifies learning patterns and challenges
- **Predictive Analytics**: Forecasts student success and potential drop-off
- **Recommendation Engine**: Suggests personalized learning paths
- **Cohort Analysis**: Compares performance across student groups

#### 4. Visualization Layer
- **Student Dashboard**: Personal progress and recommendations
- **Instructor Dashboard**: Class performance and individual student tracking
- **Analytics Reports**: Detailed insights and trends
- **Real-time Monitoring**: Live tracking of course activities

## Implementation Framework

### Database Schema

#### Student Profile Table
```sql
CREATE TABLE students (
    student_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_module INTEGER DEFAULT 1,
    overall_progress DECIMAL(5,2) DEFAULT 0.00,
    last_access TIMESTAMP,
    learning_style VARCHAR(20), -- visual, auditory, kinesthetic
    preferred_pace VARCHAR(10) -- slow, normal, fast
    status VARCHAR(10) DEFAULT 'active' -- active, inactive, completed, dropped
);
```

#### Progress Tracking Table
```sql
CREATE TABLE progress (
    progress_id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(student_id),
    module_id INTEGER,
    chapter_id INTEGER,
    exercise_id INTEGER,
    completion_percentage DECIMAL(5,2),
    time_spent INTEGER, -- in seconds
    score DECIMAL(5,2),
    attempts INTEGER DEFAULT 1,
    last_access TIMESTAMP,
    status VARCHAR(10), -- not_started, in_progress, completed, passed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Assessment Results Table
```sql
CREATE TABLE assessments (
    assessment_id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(student_id),
    module_id INTEGER,
    assessment_type VARCHAR(20), -- exercise, quiz, project, peer_review
    score DECIMAL(5,2),
    max_score DECIMAL(5,2),
    submission_date TIMESTAMP,
    feedback TEXT,
    grader_id UUID,
    status VARCHAR(10) -- submitted, graded, reviewed
);
```

### API Endpoints

#### Student Progress API
```python
from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

@app.route('/api/student/<student_id>/progress', methods=['GET'])
def get_student_progress(student_id):
    """Get comprehensive progress for a student"""
    # Implementation to fetch student progress across all modules
    progress_data = {
        "student_id": student_id,
        "overall_progress": 65.5,
        "modules": [
            {
                "module_id": 1,
                "module_name": "ROS 2 Fundamentals",
                "progress": 80.0,
                "status": "completed",
                "time_spent": 12500,  # seconds
                "completed_chapters": 4,
                "total_chapters": 5,
                "average_score": 85.0
            },
            {
                "module_id": 2,
                "module_name": "Simulation Environments",
                "progress": 45.0,
                "status": "in_progress",
                "time_spent": 8200,
                "completed_chapters": 2,
                "total_chapters": 4,
                "average_score": 78.5
            }
        ],
        "last_access": "2025-12-13T10:30:00Z",
        "estimated_completion": "2025-12-28"
    }
    return jsonify(progress_data)

@app.route('/api/student/<student_id>/progress/<module_id>', methods=['POST'])
def update_module_progress(student_id, module_id):
    """Update progress for a specific module"""
    data = request.json
    chapter_id = data.get('chapter_id')
    exercise_id = data.get('exercise_id')
    completion_percentage = data.get('completion_percentage', 0)
    time_spent = data.get('time_spent', 0)

    # Update progress in database
    # Implementation details...

    return jsonify({"status": "success", "updated_at": datetime.utcnow().isoformat()})

@app.route('/api/student/<student_id>/analytics', methods=['GET'])
def get_student_analytics(student_id):
    """Get detailed analytics for a student"""
    analytics = {
        "learning_patterns": {
            "peak_hours": ["09:00-11:00", "14:00-16:00"],
            "preferred_content": ["videos", "interactive_exercises"],
            "average_session_length": 45,  # minutes
            "engagement_score": 8.5  # out of 10
        },
        "performance_insights": {
            "strong_areas": ["ROS 2 concepts", "Basic programming"],
            "improvement_areas": ["Advanced debugging", "System integration"],
            "predicted_difficulty": "medium",
            "recommended_pace": "normal"
        },
        "recommendations": [
            "Review Chapter 3.2 on debugging techniques",
            "Spend more time on simulation exercises",
            "Join study group for Module 3"
        ]
    }
    return jsonify(analytics)
```

#### Instructor Dashboard API
```python
@app.route('/api/instructor/<instructor_id>/class/<class_id>/analytics', methods=['GET'])
def get_class_analytics(instructor_id, class_id):
    """Get comprehensive class analytics"""
    analytics = {
        "class_overview": {
            "total_students": 45,
            "active_students": 42,
            "completion_rate": 68.5,
            "average_score": 78.2,
            "drop_rate": 6.7
        },
        "module_performance": [
            {
                "module_id": 1,
                "module_name": "ROS 2 Fundamentals",
                "average_completion": 85.2,
                "average_score": 82.1,
                "difficulty_rating": "medium",
                "most_common_issues": ["Installation problems", "Concept confusion"]
            },
            {
                "module_id": 2,
                "module_name": "Simulation Environments",
                "average_completion": 72.1,
                "average_score": 75.8,
                "difficulty_rating": "hard",
                "most_common_issues": ["Performance issues", "Complex setup"]
            }
        ],
        "at_risk_students": [
            {
                "student_id": "student_123",
                "name": "John Doe",
                "progress": 25.0,
                "risk_level": "high",
                "reasons": ["Low engagement", "Missed deadlines", "Poor performance"]
            }
        ],
        "trends": {
            "weekly_progress": [65.2, 68.1, 71.5, 73.2, 75.8],  # Last 5 weeks
            "engagement_trend": "increasing",
            "performance_trend": "stable"
        }
    }
    return jsonify(analytics)
```

## Progress Tracking Implementation

### Frontend Components

#### Student Dashboard Component
```jsx
// StudentDashboard.jsx
import React, { useState, useEffect } from 'react';

const StudentDashboard = ({ studentId }) => {
  const [progress, setProgress] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetchProgressData();
    fetchAnalyticsData();
  }, [studentId]);

  const fetchProgressData = async () => {
    const response = await fetch(`/api/student/${studentId}/progress`);
    const data = await response.json();
    setProgress(data);
  };

  const fetchAnalyticsData = async () => {
    const response = await fetch(`/api/student/${studentId}/analytics`);
    const data = await response.json();
    setAnalytics(data);
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="dashboard-container">
      <div className="progress-summary">
        <h2>Overall Progress: {progress?.overall_progress}%</h2>
        <div className="progress-bar">
          <div
            className={`h-4 rounded ${getProgressColor(progress?.overall_progress)}`}
            style={{ width: `${progress?.overall_progress}%` }}
          ></div>
        </div>
      </div>

      <div className="module-progress">
        <h3>Module Progress</h3>
        {progress?.modules.map(module => (
          <div key={module.module_id} className="module-card">
            <div className="module-header">
              <h4>{module.module_name}</h4>
              <span className="progress-text">{module.progress}%</span>
            </div>
            <div className="progress-bar">
              <div
                className={`h-3 rounded ${getProgressColor(module.progress)}`}
                style={{ width: `${module.progress}%` }}
              ></div>
            </div>
            <div className="module-stats">
              <span>Time: {Math.round(module.time_spent / 3600)}h</span>
              <span>Score: {module.average_score}/100</span>
            </div>
          </div>
        ))}
      </div>

      {analytics && (
        <div className="analytics-section">
          <h3>Learning Insights</h3>
          <div className="insights-grid">
            <div className="insight-card">
              <h4>Peak Learning Hours</h4>
              <p>{analytics.learning_patterns.peak_hours.join(', ')}</p>
            </div>
            <div className="insight-card">
              <h4>Engagement Score</h4>
              <p>{analytics.learning_patterns.engagement_score}/10</p>
            </div>
            <div className="insight-card">
              <h4>Recommendations</h4>
              <ul>
                {analytics.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
```

#### Progress Tracking Hook
```javascript
// useProgressTracking.js
import { useState, useEffect } from 'react';

const useProgressTracking = (studentId, moduleId, chapterId) => {
  const [progress, setProgress] = useState(0);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime, setStartTime] = useState(Date.now());

  useEffect(() => {
    // Start tracking when component mounts
    setStartTime(Date.now());

    return () => {
      // Update progress when component unmounts
      updateProgressOnExit();
    };
  }, [studentId, moduleId, chapterId]);

  const updateProgress = async (newProgress) => {
    const currentTime = Date.now();
    const timeElapsed = Math.floor((currentTime - startTime) / 1000); // in seconds

    setProgress(newProgress);
    setTimeSpent(prev => prev + timeElapsed);

    // Send to backend
    try {
      await fetch(`/api/student/${studentId}/progress/${moduleId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chapter_id: chapterId,
          completion_percentage: newProgress,
          time_spent: timeElapsed
        })
      });
    } catch (error) {
      console.error('Failed to update progress:', error);
    }

    setStartTime(currentTime);
  };

  const updateProgressOnExit = async () => {
    const currentTime = Date.now();
    const timeElapsed = Math.floor((currentTime - startTime) / 1000);

    if (timeElapsed > 0) {
      try {
        await fetch(`/api/student/${studentId}/progress/${moduleId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            chapter_id: chapterId,
            completion_percentage: progress,
            time_spent: timeElapsed
          })
        });
      } catch (error) {
        console.error('Failed to update progress on exit:', error);
      }
    }
  };

  return { progress, timeSpent, updateProgress };
};

export default useProgressTracking;
```

## Analytics Implementation

### Data Processing Pipeline

#### Real-time Analytics Processor
```python
# analytics_processor.py
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import redis
import psycopg2
from dataclasses import dataclass

@dataclass
class ProgressEvent:
    student_id: str
    module_id: int
    chapter_id: int
    event_type: str  # 'view', 'complete', 'submit', 'interact'
    timestamp: datetime
    metadata: Dict[str, Any]

class AnalyticsProcessor:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.db_connection = psycopg2.connect(
            host="localhost",
            database="course_analytics",
            user="analytics_user",
            password="password"
        )
        self.event_queue = asyncio.Queue()

    async def process_events(self):
        """Process events from the queue in real-time"""
        while True:
            event = await self.event_queue.get()
            await self.process_single_event(event)
            self.event_queue.task_done()

    async def process_single_event(self, event: ProgressEvent):
        """Process a single progress event"""
        # Update real-time metrics
        await self.update_real_time_metrics(event)

        # Update student profile
        await self.update_student_profile(event)

        # Generate insights
        await self.generate_insights(event)

    async def update_real_time_metrics(self, event: ProgressEvent):
        """Update real-time metrics in Redis"""
        # Track active users
        current_time = datetime.utcnow()
        active_key = f"active_users:{current_time.strftime('%Y-%m-%d-%H')}"
        self.redis_client.sadd(active_key, event.student_id)
        self.redis_client.expire(active_key, 3600)  # Expire after 1 hour

        # Track module engagement
        engagement_key = f"module_engagement:{event.module_id}:{current_time.strftime('%Y-%m-%d')}"
        self.redis_client.incr(engagement_key)
        self.redis_client.expire(engagement_key, 86400)  # Expire after 1 day

    async def update_student_profile(self, event: ProgressEvent):
        """Update student profile based on activity"""
        # Calculate engagement metrics
        cursor = self.db_connection.cursor()

        # Update last activity
        cursor.execute("""
            UPDATE students
            SET last_access = %s
            WHERE student_id = %s
        """, (event.timestamp, event.student_id))

        # Update module progress
        cursor.execute("""
            INSERT INTO progress (student_id, module_id, chapter_id, completion_percentage, last_access, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_id, module_id, chapter_id)
            DO UPDATE SET
                completion_percentage = GREATEST(progress.completion_percentage, EXCLUDED.completion_percentage),
                last_access = EXCLUDED.last_access,
                status = CASE
                    WHEN EXCLUDED.completion_percentage >= 95 THEN 'completed'
                    WHEN EXCLUDED.completion_percentage > 0 THEN 'in_progress'
                    ELSE 'not_started'
                END
        """, (
            event.student_id, event.module_id, event.chapter_id,
            self.calculate_completion(event), event.timestamp,
            self.get_status_from_completion(self.calculate_completion(event))
        ))

        self.db_connection.commit()

    def calculate_completion(self, event: ProgressEvent) -> float:
        """Calculate completion percentage based on event"""
        if event.event_type == 'complete':
            return 100.0
        elif event.event_type == 'submit':
            # This would be calculated based on assessment score
            return 75.0  # Placeholder
        else:
            return 25.0  # Default for viewing/interacting

    def get_status_from_completion(self, completion: float) -> str:
        """Get status string from completion percentage"""
        if completion >= 95:
            return 'completed'
        elif completion > 0:
            return 'in_progress'
        else:
            return 'not_started'

    async def generate_insights(self, event: ProgressEvent):
        """Generate learning insights and recommendations"""
        # Calculate student engagement patterns
        engagement_score = await self.calculate_engagement_score(event.student_id)

        # Update in student profile
        cursor = self.db_connection.cursor()
        cursor.execute("""
            UPDATE students
            SET engagement_score = %s
            WHERE student_id = %s
        """, (engagement_score, event.student_id))

        self.db_connection.commit()

    async def calculate_engagement_score(self, student_id: str) -> float:
        """Calculate engagement score (0-10) for a student"""
        cursor = self.db_connection.cursor()

        # Get recent activity (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as activity_count,
                   AVG(completion_percentage) as avg_completion
            FROM progress
            WHERE student_id = %s
            AND last_access >= NOW() - INTERVAL '7 days'
        """, (student_id,))

        result = cursor.fetchone()
        if result:
            activity_count, avg_completion = result
            # Engagement score calculation (simplified)
            score = min(10.0, (activity_count * 0.5) + (avg_completion / 10.0))
            return round(score, 1)
        return 5.0  # Default score

# Initialize and start the processor
processor = AnalyticsProcessor()
asyncio.create_task(processor.process_events())
```

### Dashboard Analytics

#### Instructor Dashboard Component
```jsx
// InstructorDashboard.jsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const InstructorDashboard = ({ instructorId, classId }) => {
  const [analytics, setAnalytics] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  useEffect(() => {
    fetchClassAnalytics();
  }, [instructorId, classId, selectedTimeRange]);

  const fetchClassAnalytics = async () => {
    const response = await fetch(`/api/instructor/${instructorId}/class/${classId}/analytics?range=${selectedTimeRange}`);
    const data = await response.json();
    setAnalytics(data);
  };

  const renderModulePerformance = () => {
    if (!analytics?.module_performance) return null;

    return (
      <div className="module-performance">
        <h3>Module Performance</h3>
        <div className="performance-grid">
          {analytics.module_performance.map(module => (
            <div key={module.module_id} className="performance-card">
              <h4>{module.module_name}</h4>
              <div className="metric">
                <span className="label">Avg. Completion:</span>
                <span className="value">{module.average_completion}%</span>
              </div>
              <div className="metric">
                <span className="label">Avg. Score:</span>
                <span className="value">{module.average_score}</span>
              </div>
              <div className="metric">
                <span className="label">Difficulty:</span>
                <span className="value">{module.difficulty_rating}</span>
              </div>
              <div className="issues">
                <h5>Common Issues:</h5>
                <ul>
                  {module.most_common_issues.map((issue, idx) => (
                    <li key={idx}>{issue}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderProgressTrend = () => {
    if (!analytics?.trends?.weekly_progress) return null;

    const data = analytics.trends.weekly_progress.map((progress, index) => ({
      week: `Week ${index + 1}`,
      progress: progress
    }));

    return (
      <div className="progress-trend">
        <h3>Class Progress Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="progress" stroke="#8884d8" activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderAtRiskStudents = () => {
    if (!analytics?.at_risk_students?.length) return null;

    return (
      <div className="at-risk-students">
        <h3>At-Risk Students</h3>
        <div className="students-list">
          {analytics.at_risk_students.map(student => (
            <div key={student.student_id} className="student-card">
              <h4>{student.name}</h4>
              <div className="risk-info">
                <span className={`risk-level ${student.risk_level}`}>
                  Risk: {student.risk_level.toUpperCase()}
                </span>
                <span className="progress">Progress: {student.progress}%</span>
              </div>
              <div className="reasons">
                <h5>Reasons:</h5>
                <ul>
                  {student.reasons.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="instructor-dashboard">
      <div className="dashboard-header">
        <h1>Class Analytics Dashboard</h1>
        <div className="time-range-selector">
          <select value={selectedTimeRange} onChange={(e) => setSelectedTimeRange(e.target.value)}>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
        </div>
      </div>

      <div className="overview-stats">
        <div className="stat-card">
          <h3>Total Students</h3>
          <p>{analytics?.class_overview?.total_students || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Active Students</h3>
          <p>{analytics?.class_overview?.active_students || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Completion Rate</h3>
          <p>{analytics?.class_overview?.completion_rate || 0}%</p>
        </div>
        <div className="stat-card">
          <h3>Avg. Score</h3>
          <p>{analytics?.class_overview?.average_score || 0}</p>
        </div>
      </div>

      {renderProgressTrend()}
      {renderModulePerformance()}
      {renderAtRiskStudents()}
    </div>
  );
};

export default InstructorDashboard;
```

## Integration with Course Platform

### Event Tracking Integration
```python
# event_tracker.py
import json
import uuid
from datetime import datetime
from typing import Dict, Any

class EventTracker:
    def __init__(self, analytics_processor):
        self.processor = analytics_processor

    def track_page_view(self, student_id: str, module_id: int, chapter_id: int, page_url: str):
        """Track when a student views a page"""
        event = ProgressEvent(
            student_id=student_id,
            module_id=module_id,
            chapter_id=chapter_id,
            event_type='view',
            timestamp=datetime.utcnow(),
            metadata={
                'page_url': page_url,
                'device_type': 'web',  # Could be determined from request
                'session_id': str(uuid.uuid4())
            }
        )
        # Add to processing queue
        asyncio.create_task(self.processor.event_queue.put(event))

    def track_exercise_completion(self, student_id: str, module_id: int, chapter_id: int,
                                 exercise_id: int, score: float, time_taken: int):
        """Track completion of an exercise"""
        event = ProgressEvent(
            student_id=student_id,
            module_id=module_id,
            chapter_id=chapter_id,
            event_type='complete',
            timestamp=datetime.utcnow(),
            metadata={
                'exercise_id': exercise_id,
                'score': score,
                'time_taken': time_taken,
                'result': 'pass' if score >= 70 else 'fail'
            }
        )
        asyncio.create_task(self.processor.event_queue.put(event))

    def track_video_interaction(self, student_id: str, module_id: int, chapter_id: int,
                               video_id: str, interaction_type: str, timestamp: float):
        """Track video interactions (play, pause, seek, etc.)"""
        event = ProgressEvent(
            student_id=student_id,
            module_id=module_id,
            chapter_id=chapter_id,
            event_type='interact',
            timestamp=datetime.utcnow(),
            metadata={
                'content_type': 'video',
                'video_id': video_id,
                'interaction_type': interaction_type,
                'playback_position': timestamp
            }
        )
        asyncio.create_task(self.processor.event_queue.put(event))

    def track_discussion_participation(self, student_id: str, module_id: int,
                                     chapter_id: int, post_content: str):
        """Track participation in discussions"""
        event = ProgressEvent(
            student_id=student_id,
            module_id=module_id,
            chapter_id=chapter_id,
            event_type='interact',
            timestamp=datetime.utcnow(),
            metadata={
                'interaction_type': 'discussion_post',
                'content_length': len(post_content),
                'engagement': 'high' if len(post_content) > 100 else 'low'
            }
        )
        asyncio.create_task(self.processor.event_queue.put(event))
```

### Middleware Integration
```python
# progress_middleware.py
from functools import wraps
from flask import request, g
import uuid

def track_progress(f):
    """Decorator to automatically track progress for route handlers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract student ID from session or JWT
        student_id = get_current_student_id()

        # Extract module and chapter from URL or parameters
        module_id = kwargs.get('module_id') or request.view_args.get('module_id')
        chapter_id = kwargs.get('chapter_id') or request.view_args.get('chapter_id')

        # Track the event before executing the route
        if student_id and module_id:
            event_tracker.track_page_view(
                student_id=student_id,
                module_id=module_id,
                chapter_id=chapter_id or 1,
                page_url=request.url
            )

        return f(*args, **kwargs)
    return decorated_function

# Usage in routes
@app.route('/module/<int:module_id>/chapter/<int:chapter_id>')
@track_progress
def view_chapter(module_id, chapter_id):
    # Your route logic here
    return render_template('chapter.html', module_id=module_id, chapter_id=chapter_id)
```

## Privacy and Data Protection

### Data Anonymization
```python
# privacy_utils.py
import hashlib
from typing import Dict, Any

def anonymize_student_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Anonymize student data for analytics while preserving patterns"""
    anonymized = data.copy()

    # Replace PII with hashed values
    if 'email' in anonymized:
        anonymized['email'] = hashlib.sha256(anonymized['email'].encode()).hexdigest()[:16]

    if 'username' in anonymized:
        anonymized['username'] = hashlib.sha256(anonymized['username'].encode()).hexdigest()[:12]

    # Remove direct identifiers
    if 'student_id' in anonymized:
        # Keep a hashed version for tracking patterns
        anonymized['student_hash'] = hashlib.sha256(anonymized['student_id'].encode()).hexdigest()[:16]
        del anonymized['student_id']

    return anonymized

def aggregate_student_data(student_data_list: list) -> Dict[str, Any]:
    """Aggregate individual student data into anonymous statistics"""
    if not student_data_list:
        return {}

    # Calculate aggregate metrics
    total_students = len(student_data_list)
    avg_completion = sum(s.get('overall_progress', 0) for s in student_data_list) / total_students
    avg_time_spent = sum(s.get('total_time_spent', 0) for s in student_data_list) / total_students

    return {
        'total_students': total_students,
        'average_completion': round(avg_completion, 2),
        'average_time_spent': round(avg_time_spent, 2),
        'completion_distribution': calculate_completion_distribution(student_data_list)
    }

def calculate_completion_distribution(student_data_list: list) -> Dict[str, int]:
    """Calculate distribution of completion percentages"""
    ranges = {
        '0-25': 0,
        '26-50': 0,
        '51-75': 0,
        '76-100': 0
    }

    for student in student_data_list:
        progress = student.get('overall_progress', 0)
        if progress <= 25:
            ranges['0-25'] += 1
        elif progress <= 50:
            ranges['26-50'] += 1
        elif progress <= 75:
            ranges['51-75'] += 1
        else:
            ranges['76-100'] += 1

    return ranges
```

## Real-time Monitoring Dashboard

### WebSocket Integration for Live Updates
```python
# live_monitoring.py
from flask_socketio import SocketIO, emit
import eventlet

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    """Handle client connection for live monitoring"""
    print(f'Client connected: {request.sid}')

@socketio.on('join_class_monitoring')
def handle_join_class_monitoring(class_id):
    """Allow instructor to monitor specific class"""
    join_room(f'class_{class_id}')
    # Send initial data
    class_data = get_class_live_data(class_id)
    emit('class_data_update', class_data)

def broadcast_class_update(class_id: str, data: Dict[str, Any]):
    """Broadcast update to all monitoring clients for a class"""
    socketio.emit('class_data_update', data, room=f'class_{class_id}')

def get_class_live_data(class_id: str) -> Dict[str, Any]:
    """Get live data for a class"""
    # Get real-time metrics from Redis
    active_users = redis_client.scard(f"active_users:{datetime.utcnow().strftime('%Y-%m-%d-%H')}")
    module_engagement = {}

    for module_id in range(1, 5):  # Modules 1-4
        engagement = redis_client.get(f"module_engagement:{module_id}:{datetime.utcnow().strftime('%Y-%m-%d')}")
        module_engagement[module_id] = int(engagement) if engagement else 0

    return {
        'timestamp': datetime.utcnow().isoformat(),
        'active_users': active_users,
        'module_engagement': module_engagement,
        'total_enrolled': get_total_enrolled(class_id)
    }
```

## Performance Considerations

### Scalability Features
```python
# scalable_analytics.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aioredis

class ScalableAnalyticsProcessor:
    def __init__(self):
        self.redis_pool = aioredis.ConnectionPool.from_url("redis://localhost", max_connections=20)
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.batch_size = 100
        self.batch_queue = []

    async def process_event_batch(self, events: list):
        """Process a batch of events efficiently"""
        # Use connection pooling for Redis
        redis_conn = aioredis.Redis(connection_pool=self.redis_pool)

        # Pipeline multiple Redis operations
        pipe = redis_conn.pipeline()
        for event in events:
            self.add_to_pipeline(pipe, event)

        await pipe.execute()

        # Process database updates in batch
        await self.update_database_batch(events)

    def add_to_pipeline(self, pipe, event):
        """Add event processing to Redis pipeline"""
        # Track active users
        current_hour = datetime.utcnow().strftime('%Y-%m-%d-%H')
        pipe.sadd(f"active_users:{current_hour}", event.student_id)
        pipe.expire(f"active_users:{current_hour}", 3600)

        # Track engagement
        pipe.incr(f"module_engagement:{event.module_id}:{current_hour}")
        pipe.expire(f"module_engagement:{event.module_id}:{current_hour}", 3600)

    async def update_database_batch(self, events: list):
        """Update database with batch of events"""
        # Use async database connection
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for event in events:
                    await conn.execute("""
                        INSERT INTO progress (student_id, module_id, chapter_id, completion_percentage, last_access, status)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (student_id, module_id, chapter_id)
                        DO UPDATE SET
                            completion_percentage = GREATEST(progress.completion_percentage, EXCLUDED.completion_percentage),
                            last_access = EXCLUDED.last_access
                    """,
                    event.student_id, event.module_id, event.chapter_id,
                    self.calculate_completion(event), event.timestamp,
                    self.get_status_from_completion(self.calculate_completion(event))
                    )
```

This comprehensive progress tracking and analytics system provides:

1. **Real-time monitoring** of student progress across all modules
2. **Detailed analytics** for both students and instructors
3. **Personalized recommendations** based on learning patterns
4. **Predictive insights** to identify at-risk students
5. **Privacy protection** with data anonymization
6. **Scalable architecture** to handle large numbers of students
7. **Integration capabilities** with existing course platforms

The system is designed to be both comprehensive for instructors and helpful for students to understand their learning progress and areas for improvement.

Last updated: December 13, 2025