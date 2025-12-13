---
title: "Peer Testing and Review Mechanisms"
sidebar_label: "Peer Testing & Review"
sidebar_position: 111
---

# Peer Testing and Review Mechanisms for Exercises

## Overview

This document outlines the peer testing and review mechanisms for the Physical AI & Humanoid Robotics course exercises. Peer review is a critical component that enhances learning through collaborative assessment, diverse perspectives, and shared knowledge building.

## Peer Review System Architecture

### 1. Assignment Algorithm

#### Random Assignment with Skill Balancing
```python
# peer_assignment_algorithm.py
import random
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class AssignmentStrategy(Enum):
    RANDOM = "random"
    SKILL_BALANCED = "skill_balanced"
    ROTATION = "rotation"
    CROSS_MODULE = "cross_module"

@dataclass
class StudentProfile:
    student_id: str
    name: str
    skill_level: int  # 1-5 scale
    module_progress: Dict[int, float]  # module_id -> completion percentage
    previous_reviews: List[str]  # List of student_ids previously reviewed
    availability: bool = True

@dataclass
class ExerciseSubmission:
    submission_id: str
    student_id: str
    exercise_id: str
    module_id: int
    submission_date: str
    code_files: List[str]
    documentation: str
    test_results: Dict[str, Any]

class PeerAssignmentAlgorithm:
    def __init__(self, strategy: AssignmentStrategy = AssignmentStrategy.SKILL_BALANCED):
        self.strategy = strategy

    def assign_reviews(self, students: List[StudentProfile], submissions: List[ExerciseSubmission],
                      reviews_per_submission: int = 2) -> Dict[str, List[str]]:
        """
        Assign reviewers to submissions based on the selected strategy
        Returns: Dict mapping submission_id to list of reviewer student_ids
        """
        if self.strategy == AssignmentStrategy.RANDOM:
            return self._random_assignment(submissions, students, reviews_per_submission)
        elif self.strategy == AssignmentStrategy.SKILL_BALANCED:
            return self._skill_balanced_assignment(submissions, students, reviews_per_submission)
        elif self.strategy == AssignmentStrategy.ROTATION:
            return self._rotation_assignment(submissions, students, reviews_per_submission)
        elif self.strategy == AssignmentStrategy.CROSS_MODULE:
            return self._cross_module_assignment(submissions, students, reviews_per_submission)
        else:
            return self._random_assignment(submissions, students, reviews_per_submission)

    def _random_assignment(self, submissions: List[ExerciseSubmission], students: List[StudentProfile],
                          reviews_per_submission: int) -> Dict[str, List[str]]:
        """Random assignment of reviewers to submissions"""
        assignment = {}

        for submission in submissions:
            # Get eligible reviewers (not the submitter themselves)
            eligible_reviewers = [s for s in students if s.student_id != submission.student_id and s.availability]

            if len(eligible_reviewers) < reviews_per_submission:
                # Not enough reviewers, use all available
                reviewers = [s.student_id for s in eligible_reviewers]
            else:
                # Randomly select reviewers
                selected_reviewers = random.sample(eligible_reviewers, reviews_per_submission)
                reviewers = [s.student_id for s in selected_reviewers]

            assignment[submission.submission_id] = reviewers

        return assignment

    def _skill_balanced_assignment(self, submissions: List[ExerciseSubmission], students: List[StudentProfile],
                                  reviews_per_submission: int) -> Dict[str, List[str]]:
        """Assign reviewers with complementary skill levels"""
        assignment = {}

        for submission in submissions:
            submitter_level = next((s.skill_level for s in students if s.student_id == submission.student_id), 3)

            # Find reviewers with different skill levels for balance
            eligible_reviewers = [s for s in students
                                if s.student_id != submission.student_id
                                and s.availability
                                and s.student_id not in submission.student_id.previous_reviews]

            # Sort by skill complementarity (opposite levels are more complementary)
            complementary_reviewers = sorted(
                eligible_reviewers,
                key=lambda r: abs(submitter_level - r.skill_level),
                reverse=True
            )

            if len(complementary_reviewers) >= reviews_per_submission:
                selected_reviewers = complementary_reviewers[:reviews_per_submission]
            else:
                # Use all available reviewers
                selected_reviewers = complementary_reviewers

            assignment[submission.submission_id] = [r.student_id for r in selected_reviewers]

        return assignment

    def _rotation_assignment(self, submissions: List[ExerciseSubmission], students: List[StudentProfile],
                            reviews_per_submission: int) -> Dict[str, List[str]]:
        """Rotate assignments to ensure fair distribution"""
        assignment = {}

        # Create a rotation pattern to ensure each student reviews fairly
        all_student_ids = [s.student_id for s in students if s.availability]

        for i, submission in enumerate(submissions):
            submitter_id = submission.student_id

            # Calculate starting position in rotation
            start_idx = i % len(all_student_ids)

            # Get reviewers from rotation, skipping the submitter
            reviewers = []
            current_idx = start_idx
            while len(reviewers) < reviews_per_submission and len(reviewers) < len(all_student_ids) - 1:
                reviewer_id = all_student_ids[current_idx % len(all_student_ids)]
                if reviewer_id != submitter_id:
                    reviewers.append(reviewer_id)
                current_idx += 1

            assignment[submission.submission_id] = reviewers

        return assignment

    def _cross_module_assignment(self, submissions: List[ExerciseSubmission], students: List[StudentProfile],
                                reviews_per_submission: int) -> Dict[str, List[str]]:
        """Assign reviewers who have completed different modules"""
        assignment = {}

        for submission in submissions:
            submitter_module = submission.module_id

            # Find students who have completed different modules
            eligible_reviewers = []
            for student in students:
                if (student.student_id != submission.student_id and
                    student.availability and
                    submitter_module not in student.module_progress or
                    student.module_progress[submitter_module] < 50):  # Haven't mastered the submitter's module
                    eligible_reviewers.append(student)

            if len(eligible_reviewers) >= reviews_per_submission:
                selected_reviewers = random.sample(eligible_reviewers, reviews_per_submission)
            else:
                # Fall back to regular assignment if not enough cross-module reviewers
                all_others = [s for s in students if s.student_id != submission.student_id and s.availability]
                selected_reviewers = random.sample(all_others, min(reviews_per_submission, len(all_others)))

            assignment[submission.submission_id] = [s.student_id for s in selected_reviewers]

        return assignment
```

### 2. Review Interface and Workflow

#### Review Interface Components
```python
# review_interface.py
from flask import Flask, request, jsonify, session
from typing import Dict, List, Any
import json
from datetime import datetime

app = Flask(__name__)

class ReviewInterface:
    def __init__(self):
        self.review_templates = {
            'code_quality': {
                'title': 'Code Quality Review',
                'criteria': [
                    {'name': 'Code Structure', 'weight': 25, 'description': 'How well is the code organized?'},
                    {'name': 'Readability', 'weight': 20, 'description': 'Is the code easy to read and understand?'},
                    {'name': 'Documentation', 'weight': 20, 'description': 'Are functions and complex logic well documented?'},
                    {'name': 'Best Practices', 'weight': 20, 'description': 'Does the code follow ROS 2/Python best practices?'},
                    {'name': 'Innovation', 'weight': 15, 'description': 'Are there creative solutions or improvements?'}
                ]
            },
            'functionality': {
                'title': 'Functionality Review',
                'criteria': [
                    {'name': 'Correctness', 'weight': 30, 'description': 'Does the code work as intended?'},
                    {'name': 'Completeness', 'weight': 25, 'description': 'Does it meet all requirements?'},
                    {'name': 'Error Handling', 'weight': 20, 'description': 'How well are errors handled?'},
                    {'name': 'Performance', 'weight': 15, 'description': 'Is the code efficient?'},
                    {'name': 'Testing', 'weight': 10, 'description': 'Are there adequate tests?'}
                ]
            },
            'integration': {
                'title': 'Integration Review',
                'criteria': [
                    {'name': 'ROS 2 Integration', 'weight': 35, 'description': 'Proper use of ROS 2 concepts?'},
                    {'name': 'Communication', 'weight': 25, 'description': 'Correct topic/service usage?'},
                    {'name': 'Simulation Integration', 'weight': 20, 'description': 'Proper simulation setup?'},
                    {'name': 'Safety', 'weight': 20, 'description': 'Safety constraints implemented?'}
                ]
            }
        }

    def get_review_form(self, exercise_type: str) -> Dict[str, Any]:
        """Get the appropriate review form for the exercise type"""
        if exercise_type in self.review_templates:
            return self.review_templates[exercise_type]
        else:
            # Default to code quality template
            return self.review_templates['code_quality']

    def submit_review(self, reviewer_id: str, submission_id: str, review_data: Dict[str, Any]) -> bool:
        """Submit a peer review"""
        # Validate review data
        if not self._validate_review_data(review_data):
            return False

        # Calculate scores
        total_score = self._calculate_total_score(review_data)

        # Save review to database
        review_record = {
            'reviewer_id': reviewer_id,
            'submission_id': submission_id,
            'review_data': review_data,
            'total_score': total_score,
            'submitted_at': datetime.utcnow().isoformat(),
            'status': 'submitted'
        }

        # Store in database (implementation depends on your database)
        # save_review_to_db(review_record)

        # Update submission status
        # update_submission_review_status(submission_id)

        return True

    def _validate_review_data(self, review_data: Dict[str, Any]) -> bool:
        """Validate the submitted review data"""
        required_fields = ['criteria_scores', 'overall_feedback', 'specific_feedback']

        for field in required_fields:
            if field not in review_data:
                return False

        # Validate score ranges (0-100)
        for score in review_data['criteria_scores'].values():
            if not (0 <= score <= 100):
                return False

        return True

    def _calculate_total_score(self, review_data: Dict[str, Any]) -> float:
        """Calculate weighted total score from review"""
        criteria_scores = review_data['criteria_scores']
        criteria_weights = review_data.get('criteria_weights', {})

        if not criteria_weights:
            # Use equal weights if not specified
            return sum(criteria_scores.values()) / len(criteria_scores) if criteria_scores else 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for criterion, score in criteria_scores.items():
            weight = criteria_weights.get(criterion, 1.0)
            total_weighted_score += score * weight
            total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

review_interface = ReviewInterface()

@app.route('/api/review/form/<exercise_type>')
def get_review_form(exercise_type):
    """Get the review form for a specific exercise type"""
    form = review_interface.get_review_form(exercise_type)
    return jsonify(form)

@app.route('/api/review/submit', methods=['POST'])
def submit_review():
    """Submit a peer review"""
    data = request.json
    reviewer_id = session.get('student_id')
    submission_id = data.get('submission_id')
    review_data = data.get('review_data')

    if not reviewer_id:
        return jsonify({'error': 'Authentication required'}), 401

    success = review_interface.submit_review(reviewer_id, submission_id, review_data)

    if success:
        return jsonify({'status': 'success', 'message': 'Review submitted successfully'})
    else:
        return jsonify({'error': 'Invalid review data'}), 400
```

### 3. Review Quality Assurance

#### Automated Review Quality Checking
```python
# review_quality_checker.py
import re
from typing import Dict, List, Any
from textstat import flesch_reading_ease
import numpy as np

class ReviewQualityChecker:
    def __init__(self):
        self.min_feedback_length = 50  # Minimum characters for meaningful feedback
        self.min_constructive_score = 3.0  # Scale 1-5 for constructiveness
        self.required_elements = ['strengths', 'improvements', 'specific_examples']

    def check_review_quality(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check the quality of a peer review"""
        quality_metrics = {
            'completeness_score': self._check_completeness(review_data),
            'constructiveness_score': self._check_constructiveness(review_data),
            'specificity_score': self._check_specificity(review_data),
            'fairness_score': self._check_fairness(review_data),
            'overall_quality': 0.0
        }

        # Calculate overall quality score
        quality_metrics['overall_quality'] = np.mean([
            quality_metrics['completeness_score'],
            quality_metrics['constructiveness_score'],
            quality_metrics['specificity_score'],
            quality_metrics['fairness_score']
        ])

        quality_metrics['is_quality_review'] = quality_metrics['overall_quality'] >= 3.0

        return quality_metrics

    def _check_completeness(self, review_data: Dict[str, Any]) -> float:
        """Check if the review covers all required aspects"""
        score = 0.0
        total_required = len(self.required_elements)

        for element in self.required_elements:
            if element in review_data and review_data[element]:
                score += 1.0

        return (score / total_required) * 5.0 if total_required > 0 else 0.0

    def _check_constructiveness(self, review_data: Dict[str, Any]) -> float:
        """Check if the review is constructive and helpful"""
        feedback_text = review_data.get('overall_feedback', '') + review_data.get('specific_feedback', '')

        # Check for positive and negative balance
        positive_indicators = ['good', 'well', 'excellent', 'great', 'nice', 'effective', 'good job']
        negative_indicators = ['bad', 'poor', 'terrible', 'awful', 'needs work', 'improve']

        positive_count = sum(1 for word in positive_indicators if word.lower() in feedback_text.lower())
        negative_count = sum(1 for word in negative_indicators if word.lower() in feedback_text.lower())

        # Check for constructive suggestions
        suggestion_indicators = ['consider', 'try', 'suggest', 'recommend', 'perhaps', 'could', 'might']
        suggestion_count = sum(1 for word in suggestion_indicators if word.lower() in feedback_text.lower())

        # Calculate constructiveness score
        if suggestion_count > 0:
            return min(5.0, 2.0 + (suggestion_count * 0.5))
        elif positive_count > 0 and negative_count == 0:
            return 3.0  # Positive but not very constructive
        elif positive_count > 0 and negative_count > 0:
            return 2.5  # Balanced but could be more constructive
        else:
            return 1.0  # Not very constructive

    def _check_specificity(self, review_data: Dict[str, Any]) -> float:
        """Check if the review provides specific feedback"""
        feedback_text = review_data.get('specific_feedback', '')

        # Look for specific references (line numbers, function names, etc.)
        specific_indicators = [
            r'\bline\s+\d+',  # line references
            r'\bfunction\s+\w+',  # function references
            r'\bmethod\s+\w+',  # method references
            r'\bclass\s+\w+',  # class references
            r'\bvariable\s+\w+',  # variable references
        ]

        specific_count = 0
        for pattern in specific_indicators:
            if re.search(pattern, feedback_text, re.IGNORECASE):
                specific_count += 1

        # Check for specific examples in feedback
        if 'example' in feedback_text.lower() or 'like' in feedback_text.lower():
            specific_count += 1

        return min(5.0, specific_count * 1.5)

    def _check_fairness(self, review_data: Dict[str, Any]) -> float:
        """Check if the review is fair and unbiased"""
        criteria_scores = review_data.get('criteria_scores', {})

        if not criteria_scores:
            return 1.0  # No scores to evaluate

        scores = list(criteria_scores.values())
        mean_score = np.mean(scores)
        std_score = np.std(scores)

        # Check for extremely low or high scores (potential bias)
        if any(score < 10 or score > 95 for score in scores):
            return 2.0  # Potentially biased

        # Check for consistent scoring (fairness indicator)
        if std_score < 5:  # Very consistent scoring
            return 4.0
        elif std_score < 15:  # Reasonably consistent
            return 3.5
        else:  # Highly variable scoring
            return 2.5

    def flag_low_quality_reviews(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flag reviews that may need instructor review"""
        flagged_reviews = []

        for review in reviews:
            quality_metrics = self.check_review_quality(review)

            if quality_metrics['overall_quality'] < 2.0:
                flagged_reviews.append({
                    'review_id': review.get('review_id'),
                    'submitter_id': review.get('submitter_id'),
                    'quality_score': quality_metrics['overall_quality'],
                    'issues': self._identify_quality_issues(review)
                })

        return flagged_reviews

    def _identify_quality_issues(self, review_data: Dict[str, Any]) -> List[str]:
        """Identify specific quality issues in a review"""
        issues = []

        feedback_text = review_data.get('overall_feedback', '') + review_data.get('specific_feedback', '')

        if len(feedback_text) < self.min_feedback_length:
            issues.append(f"Feedback too short (less than {self.min_feedback_length} characters)")

        if not any(word in feedback_text.lower() for word in ['good', 'well', 'excellent', 'great']):
            issues.append("No positive feedback identified")

        if not any(word in feedback_text.lower() for word in ['improve', 'consider', 'suggest', 'recommend']):
            issues.append("No constructive suggestions identified")

        return issues
```

### 4. Conflict Resolution System

#### Review Dispute Resolution
```python
# conflict_resolution.py
from enum import Enum
from typing import Dict, List, Any
from datetime import datetime, timedelta

class DisputeStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class DisputeResolutionSystem:
    def __init__(self):
        self.dispute_threshold = 2  # Number of students who must flag a review
        self.resolution_time_limit = timedelta(days=7)  # Time to resolve disputes

    def create_dispute(self, student_id: str, review_id: str, reason: str, evidence: str = "") -> str:
        """Create a dispute for a peer review"""
        dispute_record = {
            'dispute_id': self._generate_dispute_id(),
            'student_id': student_id,
            'review_id': review_id,
            'reason': reason,
            'evidence': evidence,
            'created_at': datetime.utcnow().isoformat(),
            'status': DisputeStatus.PENDING.value,
            'flags': [student_id],  # Initially flagged by the reporter
            'resolution_notes': "",
            'resolved_at': None
        }

        # Store dispute in database
        # store_dispute(dispute_record)

        return dispute_record['dispute_id']

    def flag_review(self, student_id: str, review_id: str) -> bool:
        """Allow a student to flag a review as problematic"""
        # Get existing review flags
        # flags = get_review_flags(review_id)

        # Add student to flags if not already there
        # if student_id not in flags:
        #     add_flag(review_id, student_id)

        # Check if threshold is met
        # if len(flags) + (1 if student_id not in flags else 0) >= self.dispute_threshold:
        #     self._escalate_to_dispute(review_id)

        return True

    def _escalate_to_dispute(self, review_id: str):
        """Automatically escalate a review to dispute if threshold is met"""
        # Create dispute record
        dispute_record = {
            'dispute_id': self._generate_dispute_id(),
            'review_id': review_id,
            'reason': 'Automatic escalation - review flagged by multiple students',
            'created_at': datetime.utcnow().isoformat(),
            'status': DisputeStatus.UNDER_REVIEW.value,
            'escalation_type': 'automatic'
        }

        # Notify instructor
        # notify_instructor_of_dispute(dispute_record)

    def resolve_dispute(self, dispute_id: str, resolution: str, resolved_by: str) -> bool:
        """Resolve a dispute with a resolution"""
        # Update dispute status
        update_data = {
            'status': DisputeStatus.RESOLVED.value,
            'resolution_notes': resolution,
            'resolved_at': datetime.utcnow().isoformat(),
            'resolved_by': resolved_by
        }

        # Update dispute in database
        # update_dispute(dispute_id, update_data)

        # Apply resolution (e.g., adjust scores, provide additional review)
        # apply_resolution(dispute_id, resolution)

        return True

    def get_instructor_notifications(self) -> List[Dict[str, Any]]:
        """Get disputes that need instructor attention"""
        # Get all disputes that are pending or under review
        # disputes = get_disputes_by_status([DisputeStatus.PENDING.value, DisputeStatus.UNDER_REVIEW.value])

        # Filter by time limit
        # overdue_disputes = [
        #     d for d in disputes
        #     if datetime.utcnow() - datetime.fromisoformat(d['created_at']) > self.resolution_time_limit
        # ]

        # return overdue_disputes
        pass

    def _generate_dispute_id(self) -> str:
        """Generate a unique dispute ID"""
        import uuid
        return f"dispute_{uuid.uuid4().hex[:8]}"

    def calculate_impact_score(self, review_id: str) -> float:
        """Calculate the impact score of a review on student learning"""
        # Factors that affect impact score:
        # - Quality of the review
        # - Timeliness
        # - Specificity of feedback
        # - Constructiveness
        # - Student's perception of helpfulness

        # Implementation would aggregate various metrics
        pass
```

## Exercise-Specific Review Mechanisms

### 1. ROS 2 Exercise Reviews

#### ROS 2 Code Review Template
```python
# ros2_review_template.py
class ROS2ReviewTemplate:
    def __init__(self):
        self.review_criteria = {
            'node_design': {
                'name': 'Node Design',
                'weight': 25,
                'sub_criteria': [
                    {'name': 'Proper inheritance from Node class', 'weight': 30},
                    {'name': 'Appropriate node naming', 'weight': 20},
                    {'name': 'Clean constructor implementation', 'weight': 25},
                    {'name': 'Resource cleanup', 'weight': 25}
                ]
            },
            'communication_patterns': {
                'name': 'Communication Patterns',
                'weight': 30,
                'sub_criteria': [
                    {'name': 'Correct publisher/subscriber usage', 'weight': 40},
                    {'name': 'Appropriate message types', 'weight': 30},
                    {'name': 'Proper QoS settings', 'weight': 30}
                ]
            },
            'parameter_usage': {
                'name': 'Parameter Usage',
                'weight': 20,
                'sub_criteria': [
                    {'name': 'Parameters properly declared', 'weight': 50},
                    {'name': 'Parameter validation', 'weight': 50}
                ]
            },
            'error_handling': {
                'name': 'Error Handling',
                'weight': 15,
                'sub_criteria': [
                    {'name': 'Exception handling', 'weight': 50},
                    {'name': 'Graceful degradation', 'weight': 50}
                ]
            },
            'ros_conventions': {
                'name': 'ROS Conventions',
                'weight': 10,
                'sub_criteria': [
                    {'name': 'Naming conventions', 'weight': 50},
                    {'name': 'Package structure', 'weight': 50}
                ]
            }
        }

    def generate_review_form(self) -> Dict[str, Any]:
        """Generate a ROS 2-specific review form"""
        return {
            'exercise_type': 'ros2',
            'title': 'ROS 2 Exercise Review',
            'criteria': self.review_criteria,
            'instructions': '''
                When reviewing this ROS 2 exercise, please consider:
                - Does the code follow ROS 2 best practices?
                - Are communication patterns used correctly?
                - Is the node architecture appropriate?
                - Are there proper error handling mechanisms?
            ''',
            'rubric': self._generate_ros2_rubric()
        }

    def _generate_ros2_rubric(self) -> Dict[str, Any]:
        """Generate detailed ROS 2 rubric"""
        return {
            'excellent': {
                'description': 'Code follows all ROS 2 best practices, excellent architecture, comprehensive error handling',
                'indicators': [
                    'Proper use of ROS 2 client library',
                    'Efficient communication patterns',
                    'Comprehensive parameter validation',
                    'Excellent documentation and comments',
                    'Proper lifecycle management'
                ]
            },
            'good': {
                'description': 'Code follows most ROS 2 best practices with minor issues',
                'indicators': [
                    'Good use of ROS 2 patterns',
                    'Most communication patterns correct',
                    'Adequate error handling',
                    'Good documentation',
                    'Proper resource management'
                ]
            },
            'needs_improvement': {
                'description': 'Code has several issues with ROS 2 patterns or architecture',
                'indicators': [
                    'Issues with communication patterns',
                    'Missing error handling',
                    'Poor architecture decisions',
                    'Inadequate documentation',
                    'Resource management issues'
                ]
            },
            'unsatisfactory': {
                'description': 'Code has fundamental issues with ROS 2 concepts',
                'indicators': [
                    'Major architectural problems',
                    'Incorrect communication patterns',
                    'No error handling',
                    'Poor documentation',
                    'Resource leaks'
                ]
            }
        }

    def validate_ros2_submission(self, code: str) -> List[str]:
        """Validate basic ROS 2 code requirements"""
        issues = []

        # Check for proper imports
        if 'rclpy' not in code:
            issues.append('Missing rclpy import')

        if 'Node' not in code:
            issues.append('No Node class usage detected')

        # Check for common patterns
        if 'create_publisher' not in code and 'create_subscription' not in code:
            issues.append('No publisher or subscriber detected')

        # Check for proper initialization
        if '__init__' not in code:
            issues.append('No constructor found')

        return issues
```

### 2. Simulation Exercise Reviews

#### Gazebo/Unity Simulation Review Template
```python
# simulation_review_template.py
class SimulationReviewTemplate:
    def __init__(self):
        self.review_criteria = {
            'world_design': {
                'name': 'World Design',
                'weight': 25,
                'sub_criteria': [
                    {'name': 'Appropriate environment setup', 'weight': 40},
                    {'name': 'Realistic physics parameters', 'weight': 35},
                    {'name': 'Proper lighting and materials', 'weight': 25}
                ]
            },
            'robot_model': {
                'name': 'Robot Model',
                'weight': 30,
                'sub_criteria': [
                    {'name': 'Valid URDF/SDF model', 'weight': 30},
                    {'name': 'Appropriate joint limits', 'weight': 25},
                    {'name': 'Realistic physical properties', 'weight': 25},
                    {'name': 'Proper sensor placement', 'weight': 20}
                ]
            },
            'simulation_behavior': {
                'name': 'Simulation Behavior',
                'weight': 25,
                'sub_criteria': [
                    {'name': 'Realistic robot movement', 'weight': 40},
                    {'name': 'Proper collision detection', 'weight': 30},
                    {'name': 'Stable simulation performance', 'weight': 30}
                ]
            },
            'integration_quality': {
                'name': 'Integration Quality',
                'weight': 20,
                'sub_criteria': [
                    {'name': 'ROS 2 integration', 'weight': 50},
                    {'name': 'Control system integration', 'weight': 50}
                ]
            }
        }

    def generate_review_form(self) -> Dict[str, Any]:
        """Generate a simulation-specific review form"""
        return {
            'exercise_type': 'simulation',
            'title': 'Simulation Exercise Review',
            'criteria': self.review_criteria,
            'instructions': '''
                When reviewing this simulation exercise, please consider:
                - Does the simulation environment behave realistically?
                - Is the robot model properly configured?
                - Do the physics parameters make sense?
                - Is the integration with ROS 2 appropriate?
            ''',
            'validation_checklist': [
                'Can the simulation be launched without errors?',
                'Does the robot move as expected?',
                'Are collisions detected properly?',
                'Is the simulation stable over time?',
                'Are there appropriate sensors configured?'
            ]
        }

    def validate_simulation_submission(self, submission_files: List[str]) -> List[str]:
        """Validate simulation submission files"""
        issues = []

        # Check for required files
        has_world_file = any(f.endswith(('.world', '.sdf', '.urdf')) for f in submission_files)
        has_model_files = any('model' in f.lower() for f in submission_files)
        has_launch_files = any(f.endswith(('.launch.py', '.launch.xml')) for f in submission_files)

        if not has_world_file:
            issues.append('Missing world/simulation environment file')

        if not has_model_files:
            issues.append('Missing robot model files')

        if not has_launch_files:
            issues.append('Missing launch files for simulation')

        return issues
```

### 3. Isaac Exercise Reviews

#### Isaac Sim Review Template
```python
# isaac_review_template.py
class IsaacReviewTemplate:
    def __init__(self):
        self.review_criteria = {
            'isaac_integration': {
                'name': 'Isaac Integration',
                'weight': 30,
                'sub_criteria': [
                    {'name': 'Proper simulator setup', 'weight': 35},
                    {'name': 'Stage configuration', 'weight': 30},
                    {'name': 'Asset loading', 'weight': 35}
                ]
            },
            'ai_components': {
                'name': 'AI Components',
                'weight': 25,
                'sub_criteria': [
                    {'name': 'Perception systems', 'weight': 40},
                    {'name': 'Planning algorithms', 'weight': 35},
                    {'name': 'Control systems', 'weight': 25}
                ]
            },
            'performance_optimization': {
                'name': 'Performance Optimization',
                'weight': 20,
                'sub_criteria': [
                    {'name': 'GPU utilization', 'weight': 50},
                    {'name': 'Memory management', 'weight': 50}
                ]
            },
            'safety_considerations': {
                'name': 'Safety Considerations',
                'weight': 15,
                'sub_criteria': [
                    {'name': 'Safety constraints', 'weight': 50},
                    {'name': 'Error handling', 'weight': 50}
                ]
            },
            'documentation': {
                'name': 'Documentation',
                'weight': 10,
                'sub_criteria': [
                    {'name': 'Code comments', 'weight': 50},
                    {'name': 'Usage instructions', 'weight': 50}
                ]
            }
        }

    def generate_review_form(self) -> Dict[str, Any]:
        """Generate an Isaac-specific review form"""
        return {
            'exercise_type': 'isaac',
            'title': 'Isaac Exercise Review',
            'criteria': self.review_criteria,
            'instructions': '''
                When reviewing this Isaac exercise, please consider:
                - Is the Isaac Sim integration properly configured?
                - Do the AI components function correctly?
                - Is the solution optimized for performance?
                - Are safety considerations addressed?
            ''',
            'specialized_tools': [
                'Isaac Sim log analysis',
                'GPU performance monitoring',
                'Simulation stability testing'
            ]
        }

    def validate_isaac_submission(self, code: str) -> List[str]:
        """Validate Isaac-specific code requirements"""
        issues = []

        # Check for Isaac-specific imports
        isaac_imports = ['omni.', 'isaacsim', 'carb.']
        has_isaac_imports = any(imp in code for imp in isaac_imports)

        if not has_isaac_imports:
            issues.append('No Isaac-specific imports detected')

        # Check for simulator setup
        if 'SimulationApp' not in code:
            issues.append('SimulationApp not initialized')

        # Check for world setup
        if 'World' not in code or 'world' not in code.lower():
            issues.append('No world configuration detected')

        return issues
```

## Review Scoring and Feedback Aggregation

### 1. Scoring Algorithm

#### Weighted Average Scoring
```python
# scoring_algorithm.py
import numpy as np
from typing import Dict, List, Any

class ScoringAlgorithm:
    def __init__(self):
        self.review_weights = {
            'code_quality': 0.3,
            'functionality': 0.4,
            'documentation': 0.2,
            'innovation': 0.1
        }

    def calculate_final_score(self, submission_id: str, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate final score from multiple peer reviews"""
        if not reviews:
            return {
                'submission_id': submission_id,
                'raw_scores': [],
                'weighted_average': 0.0,
                'standard_deviation': 0.0,
                'review_count': 0,
                'status': 'pending_reviews'
            }

        # Extract scores from all reviews
        all_scores = []
        for review in reviews:
            if 'total_score' in review:
                all_scores.append(review['total_score'])

        if not all_scores:
            return {
                'submission_id': submission_id,
                'raw_scores': [],
                'weighted_average': 0.0,
                'standard_deviation': 0.0,
                'review_count': 0,
                'status': 'no_valid_scores'
            }

        # Calculate statistics
        mean_score = np.mean(all_scores)
        std_score = np.std(all_scores)
        review_count = len(all_scores)

        # Apply outlier detection and removal
        filtered_scores = self._remove_outliers(all_scores)
        final_score = np.mean(filtered_scores) if filtered_scores else mean_score

        return {
            'submission_id': submission_id,
            'raw_scores': all_scores,
            'filtered_scores': filtered_scores,
            'weighted_average': round(final_score, 2),
            'mean_before_filtering': round(mean_score, 2),
            'standard_deviation': round(std_score, 2),
            'review_count': review_count,
            'filtered_review_count': len(filtered_scores),
            'status': 'calculated'
        }

    def _remove_outliers(self, scores: List[float], threshold: float = 2.0) -> List[float]:
        """Remove outliers using standard deviation threshold"""
        if len(scores) < 3:
            return scores  # Not enough data to remove outliers reliably

        mean = np.mean(scores)
        std = np.std(scores)

        if std == 0:
            return scores  # All scores are the same

        # Keep scores within threshold standard deviations
        filtered_scores = [
            score for score in scores
            if abs(score - mean) <= threshold * std
        ]

        # Ensure we keep at least 2 scores
        if len(filtered_scores) < 2 and len(scores) >= 2:
            return scores

        return filtered_scores

    def calculate_reviewer_reliability(self, reviewer_id: str, all_reviews: List[Dict[str, Any]]) -> float:
        """Calculate reviewer reliability score based on consistency"""
        reviewer_reviews = [
            r for r in all_reviews
            if r.get('reviewer_id') == reviewer_id
        ]

        if len(reviewer_reviews) < 2:
            return 0.5  # Neutral reliability for limited data

        # Calculate consistency with other reviewers for same submissions
        consistency_scores = []
        for review in reviewer_reviews:
            submission_id = review.get('submission_id')
            if not submission_id:
                continue

            # Get other reviews for the same submission
            other_reviews = [
                r for r in all_reviews
                if r.get('submission_id') == submission_id
                and r.get('reviewer_id') != reviewer_id
            ]

            if other_reviews:
                # Calculate consistency with other reviewers
                my_score = review.get('total_score', 0)
                other_scores = [r.get('total_score', 0) for r in other_reviews]
                avg_other_score = np.mean(other_scores)

                # Consistency is higher when scores are closer
                consistency = 1.0 - min(1.0, abs(my_score - avg_other_score) / 100.0)
                consistency_scores.append(consistency)

        return np.mean(consistency_scores) if consistency_scores else 0.5
```

### 2. Feedback Aggregation

#### Constructive Feedback Compilation
```python
# feedback_aggregation.py
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any

class FeedbackAggregator:
    def __init__(self):
        self.positive_keywords = [
            'good', 'well', 'excellent', 'great', 'nice', 'effective', 'good job',
            'impressive', 'solid', 'strong', 'well done', 'perfect', 'outstanding'
        ]
        self.negative_keywords = [
            'poor', 'bad', 'terrible', 'awful', 'needs work', 'improve', 'fix',
            'incorrect', 'wrong', 'issue', 'problem', 'strange', 'confusing'
        ]
        self.suggestion_keywords = [
            'consider', 'try', 'suggest', 'recommend', 'perhaps', 'could', 'might',
            'you should', 'it would be better', 'a good idea', 'think about'
        ]

    def aggregate_feedback(self, reviews: List[Dict[str, Any]], submission_id: str) -> Dict[str, Any]:
        """Aggregate feedback from multiple peer reviews"""
        aggregated = {
            'submission_id': submission_id,
            'total_reviews': len(reviews),
            'overall_sentiment': self._calculate_sentiment(reviews),
            'common_strengths': self._extract_common_themes(reviews, 'positive'),
            'common_improvements': self._extract_common_themes(reviews, 'negative'),
            'actionable_suggestions': self._extract_suggestions(reviews),
            'feedback_summary': self._generate_summary(reviews),
            'review_quality_metrics': self._calculate_quality_metrics(reviews)
        }

        return aggregated

    def _calculate_sentiment(self, reviews: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment of reviews"""
        positive_count = 0
        negative_count = 0

        for review in reviews:
            feedback_text = review.get('overall_feedback', '') + review.get('specific_feedback', '')

            for word in self.positive_keywords:
                if word.lower() in feedback_text.lower():
                    positive_count += 1

            for word in self.negative_keywords:
                if word.lower() in feedback_text.lower():
                    negative_count += 1

        if positive_count > negative_count * 2:
            return 'positive'
        elif negative_count > positive_count * 2:
            return 'negative'
        else:
            return 'balanced'

    def _extract_common_themes(self, reviews: List[Dict[str, Any]], theme_type: str) -> List[Dict[str, Any]]:
        """Extract common themes from reviews"""
        themes = defaultdict(int)

        for review in reviews:
            feedback_text = review.get('overall_feedback', '') + review.get('specific_feedback', '')

            if theme_type == 'positive':
                keywords = self.positive_keywords
            else:
                keywords = self.negative_keywords

            for keyword in keywords:
                if keyword.lower() in feedback_text.lower():
                    # Extract context around the keyword
                    pattern = r'\b\w*\s*' + re.escape(keyword) + r'\s*\w*\b'
                    matches = re.findall(pattern, feedback_text, re.IGNORECASE)
                    for match in matches:
                        themes[match.lower()] += 1

        # Sort by frequency and return top themes
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        return [{'theme': theme, 'frequency': count} for theme, count in sorted_themes[:5]]

    def _extract_suggestions(self, reviews: List[Dict[str, Any]]) -> List[str]:
        """Extract actionable suggestions from reviews"""
        suggestions = []

        for review in reviews:
            feedback_text = review.get('specific_feedback', '')

            # Look for suggestion patterns
            suggestion_sentences = re.split(r'[.!?]+', feedback_text)
            for sentence in suggestion_sentences:
                sentence_lower = sentence.lower().strip()

                for keyword in self.suggestion_keywords:
                    if keyword in sentence_lower:
                        # Clean up the suggestion
                        suggestion = sentence.strip()
                        if suggestion and suggestion not in suggestions:
                            suggestions.append(suggestion)
                        break

        return suggestions

    def _generate_summary(self, reviews: List[Dict[str, Any]]) -> str:
        """Generate a textual summary of all feedback"""
        if not reviews:
            return "No reviews submitted yet."

        # Calculate average scores
        scores = [r.get('total_score', 0) for r in reviews if 'total_score' in r]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Count positive and negative feedback
        positive_count = sum(1 for r in reviews if self._has_positive_feedback(r))
        negative_count = sum(1 for r in reviews if self._has_negative_feedback(r))

        summary = f"Received {len(reviews)} reviews with an average score of {avg_score:.1f}/100. "
        summary += f"{positive_count} reviews highlighted strengths, {negative_count} suggested improvements."

        return summary

    def _has_positive_feedback(self, review: Dict[str, Any]) -> bool:
        """Check if a review has positive feedback"""
        feedback_text = review.get('overall_feedback', '') + review.get('specific_feedback', '')
        return any(word.lower() in feedback_text.lower() for word in self.positive_keywords)

    def _has_negative_feedback(self, review: Dict[str, Any]) -> bool:
        """Check if a review has negative feedback"""
        feedback_text = review.get('overall_feedback', '') + review.get('specific_feedback', '')
        return any(word.lower() in feedback_text.lower() for word in self.negative_keywords)

    def _calculate_quality_metrics(self, reviews: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate quality metrics for the reviews"""
        if not reviews:
            return {}

        # Average feedback length
        feedback_lengths = []
        for review in reviews:
            feedback_text = review.get('overall_feedback', '') + review.get('specific_feedback', '')
            feedback_lengths.append(len(feedback_text))

        avg_length = sum(feedback_lengths) / len(feedback_lengths) if feedback_lengths else 0

        # Calculate variety of feedback
        suggestion_counts = [self._count_suggestions(review) for review in reviews]
        avg_suggestions = sum(suggestion_counts) / len(suggestion_counts) if suggestion_counts else 0

        return {
            'average_feedback_length': avg_length,
            'average_suggestions_per_review': avg_suggestions,
            'review_helpfulness_score': min(5.0, avg_length / 50 + avg_suggestions)  # Scale 0-5
        }

    def _count_suggestions(self, review: Dict[str, Any]) -> int:
        """Count actionable suggestions in a review"""
        feedback_text = review.get('specific_feedback', '')
        suggestion_count = 0

        for keyword in self.suggestion_keywords:
            if keyword.lower() in feedback_text.lower():
                suggestion_count += 1

        return suggestion_count
```

## Quality Assurance and Moderation

### 1. Review Moderation System

#### Automated Review Moderation
```python
# review_moderation.py
from enum import Enum
from typing import Dict, List, Any
import re

class ReviewModerationStatus(Enum):
    APPROVED = "approved"
    PENDING = "pending"
    FLAGGED = "flagged"
    REJECTED = "rejected"

class ReviewModerationSystem:
    def __init__(self):
        self.prohibited_patterns = [
            r'\bfuck\b',
            r'\bshit\b',
            r'\bstupid\b',
            r'\bidiot\b',
            r'\buseless\b',
            r'\bnever\b.*\bdo\b.*\bthis\b',
            r'\byou.*\bsuck\b'
        ]
        self.min_feedback_length = 30
        self.max_feedback_length = 5000

    def moderate_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Moderate a peer review"""
        moderation_result = {
            'review_id': review_data.get('review_id'),
            'status': ReviewModerationStatus.APPROVED.value,
            'issues': [],
            'confidence': 1.0,
            'moderation_notes': []
        }

        # Check for prohibited content
        feedback_text = review_data.get('overall_feedback', '') + review_data.get('specific_feedback', '')

        for pattern in self.prohibited_patterns:
            if re.search(pattern, feedback_text, re.IGNORECASE):
                moderation_result['status'] = ReviewModerationStatus.FLAGGED.value
                moderation_result['issues'].append(f'Prohibited content detected: {pattern}')
                moderation_result['confidence'] = 1.0
                moderation_result['moderation_notes'].append('Review contains inappropriate language')
                return moderation_result

        # Check feedback length
        if len(feedback_text) < self.min_feedback_length:
            moderation_result['status'] = ReviewModerationStatus.FLAGGED.value
            moderation_result['issues'].append(f'Feedback too short: {len(feedback_text)} chars < {self.min_feedback_length}')
            moderation_result['moderation_notes'].append('Review feedback is too brief to be helpful')

        if len(feedback_text) > self.max_feedback_length:
            moderation_result['status'] = ReviewModerationStatus.FLAGGED.value
            moderation_result['issues'].append(f'Feedback too long: {len(feedback_text)} chars > {self.max_feedback_length}')
            moderation_result['moderation_notes'].append('Review feedback exceeds maximum length')

        # Check for spam patterns
        if self._detect_spam(feedback_text):
            moderation_result['status'] = ReviewModerationStatus.FLAGGED.value
            moderation_result['issues'].append('Spam content detected')
            moderation_result['moderation_notes'].append('Review appears to be spam')

        # Check for personal attacks
        if self._detect_personal_attack(feedback_text):
            moderation_result['status'] = ReviewModerationStatus.FLAGGED.value
            moderation_result['issues'].append('Personal attack detected')
            moderation_result['moderation_notes'].append('Review contains personal attacks rather than constructive feedback')

        return moderation_result

    def _detect_spam(self, text: str) -> bool:
        """Detect spam content in review"""
        # Check for repetitive content
        words = text.lower().split()
        if len(words) > 5:  # Only check if there's enough content
            word_freq = Counter(words)
            most_common_word = word_freq.most_common(1)[0] if word_freq else (None, 0)

            # If most common word appears in more than 30% of the text, it might be spam
            if most_common_word[1] / len(words) > 0.3:
                return True

        # Check for suspicious links
        link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if len(re.findall(link_pattern, text)) > 0:
            return True

        return False

    def _detect_personal_attack(self, text: str) -> bool:
        """Detect personal attacks in review"""
        personal_attack_indicators = [
            r'\byou.*\bare\b.*\b(stupid|idiot|terrible|awful|worthless)\b',
            r'\bgo.*\bto\b.*\bhell\b',
            r'\bget.*\blost\b',
            r'\buseless.*\bhuman\b',
            r'\bcan\'t.*\beven\b.*\bdo\b'
        ]

        for pattern in personal_attack_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def batch_moderate(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Moderate multiple reviews at once"""
        results = []
        for review in reviews:
            result = self.moderate_review(review)
            results.append(result)
        return results
```

This comprehensive peer testing and review system provides:

1. **Flexible Assignment Algorithms**: Multiple strategies for assigning reviewers to submissions
2. **Exercise-Specific Templates**: Tailored review forms for different exercise types (ROS 2, Simulation, Isaac)
3. **Quality Assurance**: Automated checking of review quality and constructiveness
4. **Conflict Resolution**: System for handling disputes and problematic reviews
5. **Scoring and Aggregation**: Fair scoring algorithms and feedback compilation
6. **Moderation System**: Automated content moderation to maintain review quality

The system is designed to promote constructive, educational peer reviews while maintaining fairness and quality across all course exercises.

Last updated: December 13, 2025