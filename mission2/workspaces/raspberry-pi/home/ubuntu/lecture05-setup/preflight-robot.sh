#!/usr/bin/env bash
set -eo pipefail
source /opt/ros/humble/setup.bash
source "$HOME/turtlebot3_ws/install/setup.bash"
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0 LDS_MODEL=LDS-01
exec /usr/bin/python3 "$HOME/lecture05-setup/preflight-robot.py"
