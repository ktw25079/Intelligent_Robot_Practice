#!/usr/bin/env bash
set -e
role="${1:-}"
student_id="${2:-202302200}"
student_name="${3:-강태욱}"
if [[ ! "$student_id" =~ ^[0-9]+$ ]]; then
    echo '학번은 숫자로 입력하세요.' >&2
    exit 2
fi
workspace_dir="${IRE_WS:-$HOME/ire_ws}"
source /opt/ros/humble/setup.bash
source "$workspace_dir/install/setup.bash"
export ROS_LOCALHOST_ONLY=1
case "$role" in
    talker)
        exec ros2 run my_first_pkg talker --ros-args -r "__node:=talker_${student_id}" -r "chatter:=/chatter_${student_id}" -p "student_name:=${student_name}"
        ;;
    listener)
        exec ros2 run my_first_pkg listener --ros-args -r "__node:=listener_${student_id}" -r "chatter:=/chatter_${student_id}"
        ;;
    graph)
        exec ros2 run rqt_graph rqt_graph
        ;;
    *)
        echo "Usage: $0 {talker|listener|graph} [student_id] [student_name]" >&2
        exit 2
        ;;
esac
