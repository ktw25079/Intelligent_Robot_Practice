#!/usr/bin/env bash
set -euo pipefail
exec >> /home/ubuntu/lecture05-setup/packages.log 2>&1
trap 'code=$?; echo "PACKAGE_SETUP_EXIT=$code $(date -Is)"; exit "$code"' EXIT
echo "Waiting for existing package manager: $(date -Is)"
while pgrep -x apt >/dev/null || pgrep -x apt-get >/dev/null || pgrep -x dpkg >/dev/null; do
  sleep 10
done
echo "Existing package manager finished: $(date -Is)"
dpkg --audit
if [ -n "$(dpkg --audit)" ]; then
  echo 'Existing upgrade needs attention; stopping before ROS installation.'
  exit 2
fi
export DEBIAN_FRONTEND=noninteractive
export NEEDRESTART_MODE=a
apt-get -o DPkg::Lock::Timeout=120 update
apt-get -o DPkg::Lock::Timeout=120 install -y --no-install-recommends \
  ros-humble-ros-base ros-humble-hardware-interface ros-humble-xacro \
  ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-gripper-controllers \
  ros-humble-robot-state-publisher ros-humble-dynamixel-sdk ros-humble-ros2controlcli \
  ros-humble-hls-lfcd-lds-driver ros-humble-ld08-driver \
  python3-colcon-common-extensions python3-serial build-essential git
