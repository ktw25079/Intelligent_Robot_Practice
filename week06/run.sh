#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source ./env.sh
exec ros2 launch ./mission.launch.py
