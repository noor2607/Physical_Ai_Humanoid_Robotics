#!/bin/bash
# Environment setup script for Physical AI & Humanoid Robotics Course
# This script sets up the development environment for the course

echo "Setting up Physical AI & Humanoid Robotics Course environment..."

# Check if ROS 2 is installed
if ! command -v ros2 &> /dev/null; then
    echo "ROS 2 Humble Hawksbill is not installed. Please install ROS 2 first."
    exit 1
fi

# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Create workspace if it doesn't exist
if [ ! -d "ai-textbook/workspace" ]; then
    mkdir -p ai-textbook/workspace/src
    cd ai-textbook/workspace
    echo "ROS 2 workspace created at ai-textbook/workspace"
else
    echo "ROS 2 workspace already exists"
fi

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

echo "Environment setup complete!"