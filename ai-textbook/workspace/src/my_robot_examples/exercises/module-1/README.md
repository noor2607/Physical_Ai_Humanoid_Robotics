# Module 1: ROS 2 Fundamentals - Lab Exercises

This directory contains hands-on lab exercises for Module 1: ROS 2 Fundamentals. Each exercise builds upon the concepts covered in the chapters and provides practical experience with ROS 2 fundamentals.

## Exercise List

### Exercise 1: Basic Publisher-Subscriber (Beginner)
- **Objective**: Create a simple publisher-subscriber system that exchanges messages
- **Duration**: 1-2 hours
- **Difficulty**: Beginner
- **Concepts**: Nodes, topics, publishers, subscribers

### Exercise 2: Service Client-Server (Beginner/Intermediate)
- **Objective**: Implement a request-response system using services
- **Duration**: 1.5-2.5 hours
- **Difficulty**: Beginner/Intermediate
- **Concepts**: Services, clients, servers, request-response pattern

### Exercise 3: Parameter Configuration (Intermediate)
- **Objective**: Use parameters to configure node behavior dynamically
- **Duration**: 2 hours
- **Difficulty**: Intermediate
- **Concepts**: Parameters, node configuration, dynamic reconfiguration

### Exercise 4: Action Server-Client (Intermediate)
- **Objective**: Implement a long-running task with feedback using actions
- **Duration**: 2.5-3 hours
- **Difficulty**: Intermediate
- **Concepts**: Actions, goals, feedback, result patterns

### Exercise 5: Multi-Node System Integration (Intermediate/Advanced)
- **Objective**: Integrate multiple nodes with different communication patterns
- **Duration**: 3-4 hours
- **Difficulty**: Intermediate/Advanced
- **Concepts**: Node integration, multiple communication patterns, system architecture

## Prerequisites

Before starting these exercises, ensure you have:

1. Completed the Module 1 chapters
2. Installed ROS 2 Humble Hawksbill
3. Set up your development environment
4. Created the basic workspace structure

## Exercise Structure

Each exercise follows this structure:

```
exercise-X/
├── README.md           # Exercise instructions and objectives
├── starter_code/       # Starting code files for the exercise
├── solution/           # Complete solution (for reference after attempting)
├── test_validation.py  # Validation script to check your implementation
└── requirements.txt    # Additional dependencies if needed
```

## Getting Started

1. Navigate to the specific exercise directory
2. Read the README.md for exercise objectives and requirements
3. Review the starter code if provided
4. Implement the required functionality
5. Validate your solution using the test script
6. Compare with the solution if needed (after attempting)

## Validation

Each exercise includes a validation script that checks if your implementation meets the requirements:

```bash
cd exercise-X
python3 test_validation.py
```

## Resources

- ROS 2 Documentation: https://docs.ros.org/en/humble/
- Course Chapters 1-5
- ROS 2 Tutorials: https://docs.ros.org/en/humble/Tutorials.html