# Exercise 1: Basic Publisher-Subscriber System

## Objective
Create a simple ROS 2 publisher-subscriber system that exchanges messages between nodes. The publisher will send messages containing a counter value and timestamp, while the subscriber will receive and display these messages.

## Learning Goals
- Understand the basic structure of ROS 2 nodes
- Learn how to create publishers and subscribers
- Practice using standard ROS 2 message types
- Gain familiarity with ROS 2 command-line tools

## Difficulty Level
Beginner

## Estimated Time
1-2 hours

## Prerequisites
- Completed Chapter 1 and 2 of Module 1
- ROS 2 Humble Hawksbill installed and sourced
- Basic Python programming knowledge

## Requirements

### Publisher Node (`talker`)
1. Create a node named `talker`
2. Publish `std_msgs/msg/String` messages to the topic `/chatter`
3. Send messages at 2 Hz frequency
4. Each message should contain: `"Hello World: [counter] [timestamp]"`
5. Log published messages to the console

### Subscriber Node (`listener`)
1. Create a node named `listener`
2. Subscribe to the topic `/chatter`
3. Receive `std_msgs/msg/String` messages
4. Log received messages to the console in the format: `"Received: [message_content]"`
5. Handle graceful shutdown with Ctrl+C

### Additional Requirements
1. Use proper ROS 2 Python patterns (inherit from `Node`, use `rclpy`)
2. Include proper error handling and cleanup
3. Use appropriate QoS settings for the publisher/subscriber

## Implementation Steps

1. Create a new package for the exercise:
   ```bash
   cd ~/ai-textbook/workspace/src
   ros2 pkg create --build-type ament_python basic_comms_exercise
   cd basic_comms_exercise
   ```

2. Create the talker node in `basic_comms_exercise/basic_comms_exercise/talker.py`

3. Create the listener node in `basic_comms_exercise/basic_comms_exercise/listener.py`

4. Update the `setup.py` file to include entry points for both nodes

5. Build and test your nodes:
   ```bash
   cd ~/ai-textbook/workspace
   colcon build --packages-select basic_comms_exercise
   source install/setup.bash
   ```

6. Run the publisher in one terminal:
   ```bash
   ros2 run basic_comms_exercise talker
   ```

7. Run the subscriber in another terminal:
   ```bash
   ros2 run basic_comms_exercise listener
   ```

## Validation

Your implementation is correct when:
- Messages are successfully exchanged between publisher and subscriber
- Message format matches the required format
- Both nodes handle shutdown gracefully
- You can see messages in both terminals

## Tools for Testing

- Use `ros2 topic list` to verify your topic exists
- Use `ros2 topic echo /chatter` to see messages being published
- Use `ros2 node list` to verify your nodes are running

## Solution Guide

After completing the exercise, compare your solution with the one in the `solution/` directory. Pay attention to:
- Code structure and organization
- Error handling approaches
- ROS 2 best practices implementation