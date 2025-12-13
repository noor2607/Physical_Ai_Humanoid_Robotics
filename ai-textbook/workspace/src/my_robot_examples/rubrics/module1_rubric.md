# Module 1 Assessment Rubric: ROS 2 Fundamentals

## Overview
This rubric outlines the evaluation criteria for Module 1: ROS 2 Fundamentals. The assessment evaluates students' understanding of core ROS 2 concepts including nodes, topics, services, actions, and parameters.

## Assessment Components

### 1. Basic Publisher-Subscriber System (25 points)

#### Requirements:
- Create a publisher node that sends messages at regular intervals
- Create a subscriber node that receives and processes messages
- Use appropriate ROS 2 message types
- Implement proper node lifecycle management

#### Evaluation Criteria:
- **Excellent (22-25 points)**: Publisher and subscriber work flawlessly, use proper ROS 2 patterns, include error handling and logging
- **Proficient (18-21 points)**: Core functionality works, minor issues with patterns or documentation
- **Developing (13-17 points)**: Basic functionality works but with significant issues in design or implementation
- **Beginning (0-12 points)**: Major functionality missing or not working

### 2. Service Client-Server Implementation (25 points)

#### Requirements:
- Create a service server that performs a specific task
- Create a client that calls the service and handles the response
- Implement proper error handling for service calls
- Use appropriate service message types

#### Evaluation Criteria:
- **Excellent (22-25 points)**: Service system works reliably, handles errors gracefully, follows ROS 2 best practices
- **Proficient (18-21 points)**: Core service functionality works, minor issues with error handling or design
- **Developing (13-17 points)**: Basic service functionality works but with notable issues
- **Beginning (0-12 points)**: Service implementation incomplete or non-functional

### 3. Parameter Configuration System (20 points)

#### Requirements:
- Implement a node that uses parameters for configuration
- Allow parameters to be set at launch time and modified during runtime
- Use parameter validation and callbacks appropriately
- Document parameter meanings and valid ranges

#### Evaluation Criteria:
- **Excellent (18-20 points)**: Parameter system is robust, well-documented, and handles changes gracefully
- **Proficient (15-17 points)**: Parameter functionality works with good documentation
- **Developing (11-14 points)**: Basic parameter functionality works but with issues
- **Beginning (0-10 points)**: Parameter implementation incomplete or problematic

### 4. Action Server-Client Implementation (20 points)

#### Requirements:
- Create an action server for a long-running task
- Create an action client that sends goals and handles feedback
- Implement goal cancellation capability
- Provide appropriate feedback during execution

#### Evaluation Criteria:
- **Excellent (18-20 points)**: Action system works perfectly with proper feedback and cancellation
- **Proficient (15-17 points)**: Core action functionality works well
- **Developing (11-14 points)**: Basic action functionality with some issues
- **Beginning (0-10 points)**: Action implementation incomplete or not working

### 5. System Integration and Documentation (10 points)

#### Requirements:
- Integrate multiple components into a cohesive system
- Provide clear documentation and README files
- Include proper code comments and docstrings
- Demonstrate understanding of ROS 2 architecture

#### Evaluation Criteria:
- **Excellent (9-10 points)**: Excellent integration and documentation, clear understanding of concepts
- **Proficient (7-8 points)**: Good integration and documentation
- **Developing (5-6 points)**: Basic integration and documentation
- **Beginning (0-4 points)**: Poor integration or documentation

## Grading Scale

- **A (90-100%)**: 90-100 points - Demonstrates exceptional understanding of ROS 2 concepts
- **B (80-89%)**: 80-89 points - Shows proficient understanding of ROS 2 concepts
- **C (70-79%)**: 70-79 points - Displays adequate understanding of ROS 2 concepts
- **D (60-69%)**: 60-69 points - Shows minimal understanding of ROS 2 concepts
- **F (0-59%)**: 0-59 points - Does not demonstrate adequate understanding of ROS 2 concepts

## Additional Considerations

### Bonus Points (up to 5 points)
- Implement advanced features beyond requirements
- Optimize performance or add additional functionality
- Demonstrate creative solutions to challenges

### Deductions
- **Late submission**: 5% per day late (up to 3 days allowed)
- **Plagiarism**: Immediate failure of assignment
- **Code does not compile/run**: Significant deduction depending on severity

## Submission Requirements

Students must submit:
1. Complete ROS 2 package with all source code
2. README.md with setup and usage instructions
3. Brief report explaining design decisions and challenges overcome
4. Launch file to start the complete system

## Learning Outcomes Assessment

This assessment evaluates the following learning outcomes:
- LO-M1.1: Students will be able to design, implement, and debug complex ROS 2 systems
- LO-M1.2: Students will understand ROS 2 communication patterns and best practices
- LO-M1.3: Students will create maintainable and scalable robotic software architectures

## Instructor Notes

- Run the student's system and verify each component works as specified
- Test edge cases and error conditions
- Review code quality and adherence to ROS 2 best practices
- Consider the student's understanding demonstrated through code design and documentation