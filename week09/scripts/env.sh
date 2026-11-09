#!/usr/bin/env bash
WEEK09_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/humble/setup.bash
if [[ ! -f "$WEEK09_DIR/install/setup.bash" ]]; then
  echo "먼저 week09/scripts/build.sh를 실행하세요." >&2
  return 1
fi
source "$WEEK09_DIR/install/setup.bash"
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0
export ROS_LOG_DIR="$WEEK09_DIR/log"
mkdir -p "$ROS_LOG_DIR"
