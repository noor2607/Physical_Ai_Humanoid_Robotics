---
sidebar_position: 2
title: "Chapter 1: ROS 2 Architecture and Communication Patterns"
---

# Chapter 1: ROS 2 Architecture and Communication Patterns

## Overview

In this chapter, you'll learn about the fundamental architecture of ROS 2 and how different components communicate with each other. ROS 2 provides a flexible framework for distributed computing that allows multiple processes (potentially running on different machines) to communicate with each other.

## Learning Objectives

After completing this chapter, you will be able to:
- Explain the core concepts of ROS 2 architecture
- Identify the main components of a ROS 2 system
- Understand the different communication patterns in ROS 2
- Set up a basic ROS 2 environment

## Core Concepts

### Nodes
A node is a process that performs computation. Nodes are the fundamental building blocks of a ROS 2 system. Each node runs a specific task and can communicate with other nodes through topics, services, actions, or parameters.

### Topics
Topics are named buses over which nodes exchange messages. They implement a publish-subscribe communication pattern where publishers send messages and subscribers receive them.

### Services
Services provide a request-response communication pattern. A client sends a request to a server and waits for a response.

### Actions
Actions are like services but designed for long-running tasks. They provide feedback during execution and can be canceled.

### Parameters
Parameters are configuration values that nodes can use to modify their behavior.

## ROS 2 Architecture

ROS 2 uses a distributed architecture based on the Data Distribution Service (DDS) standard. This provides:

1. **Decentralized Communication**: No single point of failure
2. **Language Independence**: Support for multiple programming languages
3. **Platform Independence**: Works across different operating systems
4. **Real-time Support**: Deterministic communication for time-critical applications

## Setting Up Your Environment

Before diving into ROS 2 concepts, make sure your environment is properly configured:

```bash
# Source the ROS 2 environment
source /opt/ros/humble/setup.bash

# Create a workspace directory
mkdir -p ~/physical_ai_ws/src
cd ~/physical_ai_ws

# Build the workspace (even if empty for now)
colcon build

# Source the workspace
source install/setup.bash
```

## Understanding the Communication Patterns

### Publish-Subscribe Pattern (Topics)

This pattern is used for streaming data where the publisher doesn't need to know who is receiving the data. It's ideal for sensor data, robot state, or any continuous stream of information.

### Request-Response Pattern (Services)

This pattern is used for direct communication where a client needs a specific response from a server. It's ideal for operations that have a clear beginning and end.

### Action Pattern

This pattern is used for long-running tasks where the client needs feedback during execution. It's ideal for navigation, manipulation, or any task that takes time to complete.

## Practical Exercise

Create a simple ROS 2 workspace and verify your installation:

1. Create a new directory for your workspace:
   ```bash
   mkdir -p ~/ros2_workspace/src
   cd ~/ros2_workspace
   ```

2. Build the empty workspace:
   ```bash
   colcon build
   ```

3. Source the workspace:
   ```bash
   source install/setup.bash
   ```

4. Check available ROS 2 commands:
   ```bash
   ros2 --help
   ```

If you see the help output, your ROS 2 environment is properly configured!

## Summary

In this chapter, you learned about the core architecture of ROS 2 and the different communication patterns it provides. You also set up your development environment and verified your installation.

In the next chapter, we'll dive deeper into nodes, topics, and services by creating practical examples.

## Resources

- [ROS 2 Documentation](https://docs.ros.org/en/humble/)
- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [DDS Specification](https://www.omg.org/spec/DDS/About-DDS/)