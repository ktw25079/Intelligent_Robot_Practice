#!/usr/bin/env bash
set -euo pipefail
export DISPLAY=${DISPLAY:-:0}
export LECTURE05_UI_MODE=staged
case ${1:-} in
  --live) export LECTURE05_UI_MODE=live ;;
  '') ;;
  *) printf 'Usage: %s [--live]\n' "$0" >&2; exit 2 ;;
esac
exec x-terminal-emulator --no-dbus --config "$HOME/ire_ws/lecture05-live/ui/terminator.conf" --layout lecture05 --maximize --title 'Lecture05 Mission2 | FOUR PANES'
