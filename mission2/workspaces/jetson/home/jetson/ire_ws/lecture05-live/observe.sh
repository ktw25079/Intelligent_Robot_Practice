#!/usr/bin/env bash
set -e
source "$HOME/ire_ws/lecture05-live/robot-env.bash"
ros2 node list --no-daemon --spin-time 3
ros2 topic list --no-daemon --spin-time 3
ros2 control list_controllers
