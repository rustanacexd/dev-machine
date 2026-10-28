#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec /opt/homebrew/bin/uv run --no-project --managed-python --python 3.14.9 "$root/bootstrap.py" "$@"
