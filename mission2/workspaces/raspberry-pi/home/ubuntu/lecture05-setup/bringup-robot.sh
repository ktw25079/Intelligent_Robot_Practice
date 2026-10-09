#!/usr/bin/env bash
# Run on the Raspberry Pi only, after arranging the arm and clearing its surroundings.
set -eo pipefail
bash "$HOME/lecture05-setup/preflight-robot.sh"
source /opt/ros/humble/setup.bash
source "$HOME/turtlebot3_ws/install/setup.bash"
source "$HOME/lecture05-repair_ws/install/setup.bash"
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0 LDS_MODEL=LDS-01
exec > >(tee "$HOME/lecture05-setup/bringup-live-fixed.log") 2>&1
exec ros2 launch turtlebot3_manipulation_bringup hardware.launch.py
