#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
[ -x /opt/homebrew/bin/brew ] || { echo "Install Homebrew first: https://brew.sh" >&2; exit 1; }
[ -x /opt/homebrew/bin/uv ] || /opt/homebrew/bin/brew install uv
exec /opt/homebrew/bin/uv run --no-project --managed-python --python 3.14.9 "$root/bootstrap.py" "$@"
