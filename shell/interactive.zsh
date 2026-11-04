# ------------------------------------------------------------------------------
# ~/.zshrc
# Built-in README for your shell setup.
#
# Load order:
# 1) Locale / Environment variables
# 2) PATH assembly (deduped)
# 3) Oh My Zsh + plugin loading
# 4) Tool initialization (fzf/terraform/gcloud/bun/starship/direnv)
# 5) Aliases
# 6) Custom functions
# 7) Local secrets file (private, machine-specific)
# ------------------------------------------------------------------------------

# 1) Locale / Environment
# Prevent locale warnings and keep UTF-8 behavior consistent across tools.
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8

# Oh My Zsh and runtime helpers.
export ZSH="$HOME/.oh-my-zsh"

# General tool behavior flags.
export ENABLE_BACKGROUND_TASKS=1
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
export DISABLE_PURE=false

export FORCE_AUTOUPDATE_PLUGINS=true

# Default editor.
export EDITOR="zed --wait"
export VISUAL="zed --wait"

# 3) oh-my-zsh + plugins
# Plugin list:
# - fzf-tab: fuzzy tab completion UI
# - zsh-bat: nicer cat-like previews through bat integration
plugins=(fzf-tab zsh-bat)
if [[ -r "$ZSH/oh-my-zsh.sh" ]]; then
    source "$ZSH/oh-my-zsh.sh"
fi

# 4) Tool Init
# Load fzf key bindings/completions only for full interactive sessions
# (avoids zle warnings when running `zsh -i -c ...`).
if [[ -o interactive && -z "$ZSH_EXECUTION_STRING" ]] && (( $+commands[fzf] )); then
  eval "$(fzf --zsh)"
fi

# Default file source for fzf if not already set by other configs.
if [[ -z "$FZF_DEFAULT_COMMAND" ]]; then
  if (( $+commands[fd] )); then
    export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
  elif (( $+commands[rg] )); then
    export FZF_DEFAULT_COMMAND='rg --files --hidden --glob "!.git/*"'
  elif (( $+commands[ag] )); then
    export FZF_DEFAULT_COMMAND='ag -l --hidden -g "" --ignore .git'
  fi
fi

# Google Cloud SDK path helper.
# This script appends Google Cloud SDK binaries to PATH when installed.
if [[ -f '/opt/homebrew/share/google-cloud-sdk/path.zsh.inc' ]]; then
  source '/opt/homebrew/share/google-cloud-sdk/path.zsh.inc'
fi

# Prompt + environment-directory hooks.
# starship: prompt renderer
# direnv: auto-loads .envrc per directory
if [[ "$TERM" != dumb ]] && (( $+commands[starship] )); then
  eval "$(starship init zsh)"
fi

if (( $+commands[direnv] )); then
  eval "$(direnv hook zsh)"
fi

# 5) Aliases
# Navigation shortcuts.
alias work="cd ~/code"
alias notes='cd ~/code/notes'
alias todo='notes && nvim go2/todo.md'

# Basic shell convenience aliases.
alias pg="ping google.com"
alias c='clear'
alias x='exit'
alias fsize='du -hs'

# Tool launch shortcuts.
alias lg='lazygit'
alias lzd='lazydocker'
alias htop="sudo /Applications/NeoHtop.app/Contents/MacOS/NeoHtop"
alias claude="claude --dangerously-skip-permissions"

# Sets ADC path in current shell for GCP SDK/client usage.
alias export_gcs_creds='export GOOGLE_APPLICATION_CREDENTIALS="/Users/rustancorpuz/.config/gcloud/application_default_credentials.json"'

# 6) Functions


# 7) Local Secrets (not committed)
[[ -f "$HOME/.zshrc.secrets" ]] && source "$HOME/.zshrc.secrets"

# bun completions
[ -s "/Users/rustancorpuz/.bun/_bun" ] && source "/Users/rustancorpuz/.bun/_bun"

# browser-use CLI: do not prepend ~/.browser-use-env to PATH globally — it hijacks
# `python` for every shell. Use `uv run` / project venvs for Python, or activate
# that env only when working on browser-use.



# sentry
fpath=("/Users/rustancorpuz/.local/share/zsh/site-functions" $fpath)
