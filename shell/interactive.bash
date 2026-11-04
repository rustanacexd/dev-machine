. "$HOME/.config/dev-machine/shell/env.sh"
if command -v wt >/dev/null 2>&1; then
    eval "$(command wt config shell init bash)"
fi
