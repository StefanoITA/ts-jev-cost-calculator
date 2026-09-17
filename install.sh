#!/usr/bin/env sh
# One-step installer for ts-jev-cost-calculator (provides the `ts-jev-cost-calculator` and `tscost` commands).
# Usage:  sh install.sh            (from the package folder)
#         sh install.sh /path/to/ts-jev-cost-calculator
# Picks the first available of: uv, pipx, pip (--user). Nothing else to configure.
set -e
SRC="${1:-$(cd "$(dirname "$0")" && pwd)}"
if command -v uv >/dev/null 2>&1; then
  uv tool install --force --reinstall "$SRC"
elif command -v pipx >/dev/null 2>&1; then
  pipx install --force "$SRC"
elif command -v python3 >/dev/null 2>&1; then
  python3 -m pip install --user --upgrade "$SRC" 2>/dev/null || python3 -m pip install --user --upgrade --break-system-packages "$SRC"
else
  echo "error: no uv, pipx or python3 found. Install Python 3.9+ first." >&2; exit 1
fi
echo
if command -v tscost >/dev/null 2>&1; then
  tscost info
else
  echo "Installed, but the commands are not on your PATH yet. Add ~/.local/bin to PATH, e.g.:"
  echo '  export PATH="$HOME/.local/bin:$PATH"'
fi
