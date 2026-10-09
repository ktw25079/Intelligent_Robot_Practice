# ROS/IRE environment. AI venv is activated separately when needed.
source /opt/ros/humble/setup.bash
if [ -f "$HOME/.local/opt/gazebo11/share/gazebo-11/setup.sh" ]; then
  export GAZEBO_INSTALL_PREFIX="$HOME/.local/opt/gazebo11"
  export PATH="$GAZEBO_INSTALL_PREFIX/bin:$PATH"
  export LD_LIBRARY_PATH="$GAZEBO_INSTALL_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  export CMAKE_PREFIX_PATH="$GAZEBO_INSTALL_PREFIX${CMAKE_PREFIX_PATH:+:$CMAKE_PREFIX_PATH}"
  export PKG_CONFIG_PATH="$GAZEBO_INSTALL_PREFIX/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
  source "$GAZEBO_INSTALL_PREFIX/share/gazebo-11/setup.sh"
elif [ -f /usr/share/gazebo/setup.sh ]; then
  source /usr/share/gazebo/setup.sh
fi
if [ -f "$HOME/ire_ws/install/setup.bash" ]; then
  source "$HOME/ire_ws/install/setup.bash"
fi
export TURTLEBOT3_MODEL=waffle_pi
