#!/usr/bin/env bash
# Run the ROS 2 installation-check demos in separate terminals.
set -e
case "${1:-}" in
    talker|listener) role="$1" ;;
    *) echo "Usage: $0 {talker|listener}" >&2; exit 2 ;;
esac
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=1
if [[ "$role" == talker ]]; then
    exec ros2 run demo_nodes_cpp talker
else
    exec ros2 run demo_nodes_py listener
fi
