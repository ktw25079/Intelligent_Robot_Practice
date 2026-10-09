#!/usr/bin/env bash
set -u
role=${1:?pane role required}
mode=${LECTURE05_UI_MODE:-staged}
base=$HOME/ire_ws/lecture05-live
case "$role" in
  bringup) title='1 | Pi SBC | hardware.launch.py'; shown='ssh ubuntu@192.168.0.21  →  bash ~/lecture05-setup/bringup-robot.sh' ;;
  monitor) title='2 | Jetson | /cmd_vel'; shown='ros2 topic echo /cmd_vel' ;;
  servo) title='3 | Jetson | MoveIt Servo'; shown='ros2 launch turtlebot3_manipulation_moveit_config servo.launch.py use_sim:=false' ;;
  teleop) title='4 | Jetson | Keyboard teleop'; shown='ros2 run turtlebot3_manipulation_teleop turtlebot3_manipulation_teleop' ;;
  *) exit 2 ;;
esac
printf '\033]0;%s\007' "$title"
printf '\033[1;36m%s\033[0m\n\n%s\n\n' "$title" "$shown"
printf 'ROS_DOMAIN_ID=4 | ROS_LOCALHOST_ONLY=0 | real robot\n\n'
if [[ $mode != live ]]; then
  printf 'PREPARED — this pane has NOT started ROS or robot motion.\n'
  printf 'After bringup verification, reopen with: bash %s/ui/launch-four-pane.sh --live\n' "$base"
  exec bash --noprofile --norc
fi
case "$role" in
  bringup)
    if [[ ${LECTURE05_SBC_VIEW:-launch} == attach ]]; then
      ssh -tt -S /home/jetson/.ssh/lecture05-arm-fixed ubuntu@192.168.0.21 'tmux attach-session -r -t lecture05-bringup'
    else
      ssh -tt -S /home/jetson/.ssh/lecture05-arm-fixed ubuntu@192.168.0.21 'bash ~/lecture05-setup/bringup-robot.sh'
    fi ;;
  monitor) set +u; source "$base/robot-env.bash"; ros2 topic echo /cmd_vel ;;
  servo) bash "$base/servo.sh" ;;
  teleop)
    printf 'Click THIS pane for keys: i/k forward/back | j/l turn | SPACE stop\n'
    printf 'Arm: 1-4 / qwer | Gripper: o/p | ESC quit\n\n'
    bash "$base/teleop.sh" ;;
esac
status=$?
printf '\nProcess ended (exit %s). Review output above.\n' "$status"
exec bash --noprofile --norc
