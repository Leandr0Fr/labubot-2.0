#!/usr/bin/env bash
# Regenera las maquetas y sus PNG en docs/telegram/capturas/, en tema oscuro.
# Uso (Git Bash): bash docs/telegram/capturas/src/capturar.sh [01-start-pendiente ...]
set -euo pipefail

cd "$(dirname "$0")"
chrome="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"

node build.mjs

if [ "$#" -eq 0 ]; then
  set -- $(ls [0-9]*.html | sed 's/\.html$//')
fi

for name in "$@"; do
  "$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size=390,844 --virtual-time-budget=4000 \
    --screenshot="$(cygpath -w "$PWD/../$name.png")" \
    "file:///$(cygpath -m "$PWD/$name.html")#dark" 2>/dev/null
  echo "$name.png"
done
