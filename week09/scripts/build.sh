#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")/.."
source /opt/ros/humble/setup.bash
source_dir="../mission2/workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation"
colcon build --symlink-install --base-paths   "$source_dir/turtlebot3_manipulation_description"   "$source_dir/turtlebot3_manipulation_bringup"   "$source_dir/turtlebot3_manipulation_cartographer"   "$source_dir/turtlebot3_manipulation_moveit_config"   turtlebot3_manipulation_teleop --cmake-args -DBUILD_TESTING=OFF
