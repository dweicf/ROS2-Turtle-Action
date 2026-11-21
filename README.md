# ROS2-Turtle-Action

A ROS 2 Humble learning project based on Python Action communication.

## 1. Project Overview

This project implements a TurtleSim navigation system
using ROS 2 Action communication.

Main features:

- Custom Action interface
- Action Server and Action Client
- Goal, Feedback and Result
- Multi-point sequential navigation
- Manual goal cancellation
- MultiThreadedExecutor
- ReentrantCallbackGroup
- Launch file configuration
- Runtime parameter configuration

## 2. Environment

- Ubuntu 22.04
- ROS 2 Humble
- Python 3
- TurtleSim

## 3. Package Structure

```text
turtle_action_ws/
├── src/
│   ├── turtle_action_demo/
│   │   ├── launch/
│   │   ├── turtle_action_demo/
│   │   ├── package.xml
│   │   └── setup.py
│   │
│   └── turtle_action_interfaces/
│       ├── action/
│       │   └── MoveToPosition.action
│       ├── CMakeLists.txt
│       └── package.xml
│
├── README.md
└── .gitignore