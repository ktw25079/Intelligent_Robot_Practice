#!/usr/bin/env bash
set -euo pipefail
export DISPLAY=${DISPLAY:-:0}
window=$(xdotool search --onlyvisible --name '^Lecture05 Mission2 \| FOUR PANES$' | tail -n 1)
[[ -n "$window" ]]
xdotool windowactivate --sync "$window"
output=${1:-"$HOME/ire_ws/lecture05-live/ui/mission2-$(date +%Y%m%d-%H%M%S).png"}
scrot -u "$output"
printf '%s\n' "$output"
