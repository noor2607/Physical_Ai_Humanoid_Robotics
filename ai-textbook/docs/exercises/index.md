---
sidebar_position: 1
title: "Course Exercises"
---

# Course Exercises: Hands-On Learning

This section contains hands-on exercises for all course modules. Each exercise is designed to reinforce the concepts learned in the chapters through practical implementation.

## Module 1 Exercises: ROS 2 Fundamentals

### Exercise 1: Basic Publisher-Subscriber System

**Objective**: Create a basic ROS 2 publisher-subscriber system that exchanges messages between nodes.

**Requirements**:
- Create a publisher node that sends messages at regular intervals
- Create a subscriber node that receives and processes messages
- Use appropriate ROS 2 message types
- Implement proper node lifecycle management

**Files to reference**:
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/talker.py` - Example publisher
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/listener.py` - Example subscriber
- `ai-textbook/workspace/src/my_robot_examples/exercises/module-1/exercise-1/README.md` - Exercise instructions
- `ai-textbook/workspace/src/my_robot_examples/exercises/module-1/exercise-1/solution/` - Solution files
- `ai-textbook/workspace/src/my_robot_examples/exercises/module-1/exercise-1/validate_exercise1.py` - Validation script

### Exercise 2: Service Client-Server Implementation

**Objective**: Implement a service-based communication system between nodes.

**Requirements**:
- Create a service server that performs a specific task
- Create a client that calls the service and handles the response
- Implement proper error handling for service calls
- Use appropriate service message types

**Files to reference**:
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/add_two_ints_server.py` - Example service server
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/add_two_ints_client.py` - Example service client

### Exercise 3: Action Server-Client Implementation

**Objective**: Create an action-based system for long-running tasks with feedback.

**Requirements**:
- Create an action server for a long-running task
- Create an action client that sends goals and handles feedback
- Implement goal cancellation capability
- Provide appropriate feedback during execution

**Files to reference**:
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/fibonacci_action_server.py` - Example action server
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/fibonacci_action_client.py` - Example action client

### Exercise 4: Parameter Configuration System

**Objective**: Implement a node that uses parameters for configuration.

**Requirements**:
- Implement a node that uses parameters for configuration
- Allow parameters to be set at launch time and modified during runtime
- Use parameter validation and callbacks appropriately
- Document parameter meanings and valid ranges

**Files to reference**:
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/parameter_node.py` - Example parameter-based node

### Exercise 5: System Integration

**Objective**: Integrate multiple components into a cohesive system.

**Requirements**:
- Combine publisher, subscriber, service, and action components
- Demonstrate understanding of ROS 2 architecture
- Include proper documentation and error handling

**Files to reference**:
- `ai-textbook/workspace/src/my_robot_examples/my_robot_examples/robot_controller.py` - Comprehensive example
- `ai-textbook/workspace/src/my_robot_examples/rubrics/module1_rubric.md` - Assessment rubric

## Module 4 Exercises: Voice-Controlled Robotics

### Lab Exercise 1: Advanced Voice Command Processing

**Objective**: Implement an advanced voice command processing system that can handle complex natural language commands, maintain context, and execute multi-step tasks in Isaac Sim.

**Requirements**:
- Implement advanced speech recognition with noise filtering
- Create context-aware natural language understanding
- Develop multi-step task decomposition from voice commands
- Integrate with Isaac Sim for complex task execution

**Files to reference**:
- `ai-textbook/workspace/exercises/module-4/lab-exercise-1-voice-command-processing.md` - Exercise instructions
- `ai-textbook/workspace/src/my_robot_examples/voice_control/voice_to_action.py` - Voice processing implementation
- `ai-textbook/workspace/exercises/module-4/validation/validate_lab1_voice_processing.py` - Validation script

### Lab Exercise 2: LLM Integration for Robotic Reasoning

**Objective**: Implement a sophisticated system that integrates Large Language Models (LLMs) with robotic reasoning for complex task planning and execution.

**Requirements**:
- Integrate LLMs with robotic planning systems
- Implement context-aware reasoning for task execution
- Create effective prompt engineering for robotics applications
- Evaluate LLM performance for robotic reasoning tasks

**Files to reference**:
- `ai-textbook/workspace/exercises/module-4/lab-exercise-2-llm-robotic-reasoning.md` - Exercise instructions
- `ai-textbook/workspace/src/my_robot_examples/voice_control/llm_integration.py` - LLM integration implementation
- `ai-textbook/workspace/exercises/module-4/validation/validate_lab2_llm_reasoning.py` - Validation script

### Lab Exercise 3: Cognitive Planning and Task Execution

**Objective**: Implement a sophisticated cognitive planning system that bridges high-level natural language commands with low-level robot actions using hierarchical task networks.

**Requirements**:
- Implement hierarchical task networks for complex goal decomposition
- Create symbolic planning systems that work with robotic execution
- Develop execution monitoring and failure recovery mechanisms
- Integrate planning with real-time robotic control systems

**Files to reference**:
- `ai-textbook/workspace/exercises/module-4/lab-exercise-3-cognitive-planning.md` - Exercise instructions
- `ai-textbook/workspace/src/my_robot_examples/voice_control/cognitive_planning.py` - Cognitive planning implementation
- `ai-textbook/workspace/exercises/module-4/validation/validate_lab3_cognitive_planning.py` - Validation script

### Lab Exercise 4: Multi-Modal Integration and Safety

**Objective**: Implement a comprehensive multi-modal integration system that combines voice commands, visual perception, and safety mechanisms for robust conversational robotics.

**Requirements**:
- Integrate multiple sensory modalities (voice, vision, touch) for robotic control
- Implement comprehensive safety systems and validation mechanisms
- Create robust perception-action loops with uncertainty handling
- Develop fail-safe mechanisms for autonomous robot operation

**Files to reference**:
- `ai-textbook/workspace/exercises/module-4/lab-exercise-4-multi-modal-integration-safety.md` - Exercise instructions
- `ai-textbook/workspace/exercises/module-4/validation/validate_lab4_multi_modal_safety.py` - Validation script

### Lab Exercise 5: Capstone Integration and Evaluation

**Objective**: Integrate all components developed in previous modules to create a complete voice-controlled humanoid robot system and evaluate end-to-end performance.

**Requirements**:
- Integrate all voice, LLM, planning, and control components into a cohesive system
- Evaluate end-to-end system performance and effectiveness
- Analyze system bottlenecks and optimization opportunities
- Assess real-world applicability and limitations of the approach

**Files to reference**:
- `ai-textbook/workspace/exercises/module-4/lab-exercise-5-capstone-integration-evaluation.md` - Exercise instructions
- `ai-textbook/workspace/exercises/module-4/validation/validate_lab5_capstone_integration.py` - Validation script

## Validation and Assessment

To validate your exercises, use the provided validation scripts in the workspace:

For Module 1 exercises:
```bash
cd ai-textbook/workspace
source install/setup.bash  # Or your ROS 2 environment setup
python3 src/my_robot_examples/exercises/module-1/exercise-1/validate_exercise1.py
```

For Module 4 exercises:
```bash
cd ai-textbook/workspace/exercises/module-4/validation
python3 run_all_validations.py --all
```

Your work will be assessed according to the rubrics found at:
- `ai-textbook/workspace/src/my_robot_examples/rubrics/module1_rubric.md` - Module 1 rubric
- `ai-textbook/workspace/docs/module-4-vla/assessment-project-requirements.md` - Module 4 assessment requirements