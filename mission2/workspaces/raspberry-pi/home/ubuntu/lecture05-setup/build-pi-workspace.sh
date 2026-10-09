#!/usr/bin/env bash
set -eo pipefail
exec >> "$HOME/lecture05-setup/build.log" 2>&1
echo "Waiting for ROS packages: $(date -Is)"
while ! grep -q '^PACKAGE_SETUP_EXIT=' "$HOME/lecture05-setup/packages.log"; do sleep 10; done
if ! grep -q '^PACKAGE_SETUP_EXIT=0 ' "$HOME/lecture05-setup/packages.log"; then
  echo 'Package installation failed; build not started.'
  exit 2
fi
source /opt/ros/humble/setup.bash
cd "$HOME/turtlebot3_ws"
export MAKEFLAGS=-j1
colcon build --symlink-install --executor sequential \
  --packages-select turtlebot3_manipulation_description turtlebot3_manipulation_hardware turtlebot3_manipulation_bringup \
  --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
source install/setup.bash
ros2 pkg prefix turtlebot3_manipulation_bringup
ros2 pkg prefix turtlebot3_manipulation_hardware
ros2 pkg prefix hls_lfcd_lds_driver
ros2 pkg prefix ld08_driver
ldd install/turtlebot3_manipulation_hardware/lib/libturtlebot3_manipulation_hardware.so
printf 'BUILD_SETUP_SUCCESS %s\n' "$(date -Is)"
