#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")/.."
case "${1:-help}" in
  help) echo '사용: bash scripts/run.sh {map|servo|teleop|save}'; exit 0 ;;
  map|servo|teleop|save) ;;
  *) echo '알 수 없는 명령입니다.' >&2; exit 2 ;;
esac
source scripts/env.sh
case "$1" in
  map) exec ros2 launch turtlebot3_manipulation_cartographer cartographer.launch.py ;;
  servo) exec ros2 launch turtlebot3_manipulation_moveit_config servo.launch.py use_sim:=false ;;
  teleop) exec ros2 run turtlebot3_manipulation_teleop turtlebot3_manipulation_teleop ;;
  save)
    mkdir -p results/sessions
    dest="$PWD/results/sessions/$(date +%Y%m%d_%H%M%S)"
    mkdir "$dest"
    ros2 run nav2_map_server map_saver_cli -f "$dest/map" --ros-args -p use_sim_time:=false -p save_map_timeout:=10.0
    test -s "$dest/map.pgm" && test -s "$dest/map.yaml"
    echo "저장 완료: $dest"
    ;;
esac
