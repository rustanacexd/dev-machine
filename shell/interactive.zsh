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

# 3) Completion + oh-my-zsh libraries and plugins
# Loaded directly instead of through oh-my-zsh.sh, which spent ~40 ms on
# update checks, compaudit, and zcompdump bookkeeping. shell-repositories.json
# pins the oh-my-zsh revision, so its updater has nothing to do.
# Plugin list:
# - fzf-tab: fuzzy tab completion UI
# - zsh-bat: nicer cat-like previews through bat integration
ZSH_CUSTOM="$ZSH/custom"
ZSH_CACHE_DIR="$ZSH/cache"
plugins=(fzf-tab zsh-bat)
fpath=("$ZSH_CUSTOM"/plugins/${^${(Oa)plugins}} "$ZSH"/{functions,completions} "$ZSH_CUSTOM"/{functions,completions}
       "$ZSH_CACHE_DIR/completions" "$HOME/.local/share/zsh/site-functions" $fpath)

# compinit -C skips the per-startup fpath scan. Rebuild the dump daily, or
# when fpath changes, so newly installed completions still appear.
ZSH_COMPDUMP="${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump-$ZSH_VERSION"
autoload -Uz compinit
_zcompdump_fresh=("$ZSH_COMPDUMP"(N.mh-24))
if (( $#_zcompdump_fresh )) && [[ -r "$ZSH_COMPDUMP.fpath" && "$(<"$ZSH_COMPDUMP.fpath")" == "$fpath" ]]; then
  compinit -C -d "$ZSH_COMPDUMP"
else
  mkdir -p "${ZSH_COMPDUMP:h}"
  rm -f "$ZSH_COMPDUMP"
  compinit -i -d "$ZSH_COMPDUMP"
  print -r -- "$fpath" >| "$ZSH_COMPDUMP.fpath"
  zcompile "$ZSH_COMPDUMP"
fi
unset _zcompdump_fresh

for _omz_file in "$ZSH"/lib/*.zsh; do source "$_omz_file"; done
for _omz_file in $plugins; do source "$ZSH_CUSTOM/plugins/$_omz_file/$_omz_file.plugin.zsh"; done
for _omz_file in "$ZSH_CUSTOM"/*.zsh(N); do source "$_omz_file"; done
unset _omz_file
[[ -z "$LS_COLORS" ]] || zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"

# 4) Tool Init
# Sources a tool's generated init script from a cache keyed by the resolved
# binary path, so an upgrade (a new Cellar path) regenerates it.
_cached_init() {
  local cache="${XDG_CACHE_HOME:-$HOME/.cache}/zsh/init-$1-${${commands[$1]:A}//\//%}.zsh"
  if [[ ! -s "$cache" ]]; then
    rm -f "${cache:h}/init-$1-"*(N)
    "$@" >| "$cache" || { rm -f "$cache"; return 1 }
  fi
  source "$cache"
}

# Load fzf key bindings/completions only for full interactive sessions
# (avoids zle warnings when running `zsh -i -c ...`).
if [[ -o interactive && -z "$ZSH_EXECUTION_STRING" ]] && (( $+commands[fzf] )); then
  _cached_init fzf --zsh
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
  _cached_init starship init zsh
fi

if (( $+commands[direnv] )); then
  _cached_init direnv hook zsh
fi
unfunction _cached_init

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


