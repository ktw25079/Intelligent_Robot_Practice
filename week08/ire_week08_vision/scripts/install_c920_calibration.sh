#!/usr/bin/env bash
set -e
VISION_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
CALIB_DOWNLOAD=$(mktemp -d /tmp/c920-calibration.XXXXXX)
trap 'rm -rf "$CALIB_DOWNLOAD"' EXIT
mkdir -p "$VISION_ROOT/.local-tools/camera-calibration"
cd "$CALIB_DOWNLOAD"
apt-get download ros-humble-camera-calibration python3-semver
for package in *.deb; do
  dpkg-deb -x "$package" "$VISION_ROOT/.local-tools/camera-calibration"
done
"$VISION_ROOT/scripts/calibrate_c920.sh" --help >/dev/null
echo "C920 calibration tool installed and executable."
