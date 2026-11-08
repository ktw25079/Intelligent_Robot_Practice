#!/usr/bin/env bash
set -e
VISION_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CALIB_ROOT="$VISION_ROOT/.local-tools/camera-calibration"
source /opt/ros/humble/setup.bash
export AMENT_PREFIX_PATH="$CALIB_ROOT/opt/ros/humble${AMENT_PREFIX_PATH:+:$AMENT_PREFIX_PATH}"
export PYTHONPATH="$CALIB_ROOT/opt/ros/humble/lib/python3.10/site-packages:$CALIB_ROOT/usr/lib/python3/dist-packages${PYTHONPATH:+:$PYTHONPATH}"
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0
if [[ ${1:-} == --help ]]; then
  exec ros2 run camera_calibration cameracalibrator --help
fi
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 SQUARE_SIZE_METERS (measured side of ONE checkerboard square)" >&2
  exit 2
fi
python3 -c 'import sys,math; x=float(sys.argv[1]); assert math.isfinite(x) and x>0, "Square size must be positive"' "$1"
exec ros2 run camera_calibration cameracalibrator --size 8x6 --square "$1" \
  --camera_name hd_pro_webcam_c920 --no-service-check --ros-args \
  -r image:=/logitech/image_raw \
  -r camera/set_camera_info:=/logitech/set_camera_info
