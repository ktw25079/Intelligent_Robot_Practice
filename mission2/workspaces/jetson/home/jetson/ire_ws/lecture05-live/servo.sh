#!/usr/bin/env bash
set -e
source "$HOME/ire_ws/lecture05-live/robot-env.bash"
exec ros2 launch turtlebot3_manipulation_moveit_config servo.launch.py use_sim:=false
