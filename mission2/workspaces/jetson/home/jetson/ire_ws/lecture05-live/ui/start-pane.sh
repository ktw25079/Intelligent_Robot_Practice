#!/usr/bin/env bash
# Only use on a PREPARED shell pane; never type into an active teleop process.
set -euo pipefail
export DISPLAY=${DISPLAY:-:0}
role=${1:?Usage: start-pane.sh bringup|monitor|servo|teleop}
case "$role" in
 bringup) column=0; row=0 ;;
 monitor) column=1; row=0 ;;
 servo) column=0; row=1 ;;
 teleop) column=1; row=1 ;;
 *) exit 2 ;;
esac
window=$(xdotool search --onlyvisible --name '^Lecture05 Mission2 \| FOUR PANES$' | tail -n 1)
[[ -n "$window" ]]
eval "$(xdotool getwindowgeometry --shell "$window")"
x=$((WIDTH * (1 + 2 * column) / 4))
y=$((HEIGHT * (1 + 2 * row) / 4))
xdotool windowactivate --sync "$window"
xdotool mousemove --window "$window" "$x" "$y" click 1
xdotool type --clearmodifiers --delay 2 "LECTURE05_UI_MODE=live bash /home/jetson/ire_ws/lecture05-live/ui/pane.sh $role"
xdotool key --clearmodifiers Return
