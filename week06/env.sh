#!/usr/bin/env bash
# Source this file in every terminal used for the simulation.
WEEK06_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TB3_SIM_WS="${TB3_SIM_WS:-$HOME/tb3_sim_ws}"
source /opt/ros/humble/setup.bash
if [[ ! -f "$TB3_SIM_WS/install/setup.bash" ]]; then
    echo "Build the simulation workspace first: $TB3_SIM_WS" >&2
    return 1
fi
source "$TB3_SIM_WS/install/setup.bash"
source /usr/share/gazebo/setup.sh
export ROS_DOMAIN_ID=66 ROS_LOCALHOST_ONLY=1
export GAZEBO_MASTER_URI=http://127.0.0.1:11366
export TURTLEBOT3_MODEL=waffle_pi
export ROS_LOG_DIR="$WEEK06_DIR/log"
