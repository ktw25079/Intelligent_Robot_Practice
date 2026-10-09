#!/usr/bin/env bash
set -e
source "$HOME/ire_ws/lecture05-live/robot-env.bash"
exec ros2 run turtlebot3_manipulation_teleop turtlebot3_manipulation_teleop
