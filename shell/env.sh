_dev_path=
_dev_candidates="$HOME/.local/share/dev-machine/npm/bin:$HOME/.venvs/default/bin:$HOME/.local/bin:$HOME/.local/share/mise/shims:$HOME/Library/pnpm/bin:$HOME/.cargo/bin:$HOME/go/bin:$HOME/.orbstack/bin:$HOME/.codeium/windsurf/bin:/opt/homebrew/opt/openssl@3/bin:/opt/homebrew/opt/ffmpeg-full/bin:/opt/homebrew/opt/imagemagick-full/bin:/opt/homebrew/share/google-cloud-sdk/bin:/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
if [ -n "${VIRTUAL_ENV:-}" ] && [ -d "$VIRTUAL_ENV/bin" ]; then
    _dev_candidates="$VIRTUAL_ENV/bin:$_dev_candidates"
fi
while [ -n "$_dev_candidates" ]; do
    _dev_dir=${_dev_candidates%%:*}
    if [ "$_dev_candidates" = "$_dev_dir" ]; then
        _dev_candidates=
    else
        _dev_candidates=${_dev_candidates#*:}
    fi
    [ -n "$_dev_dir" ] || continue
    case "$_dev_dir" in
        "$HOME"/.nvm/versions/node/*/bin|"$HOME"/.pyenv/shims|"$HOME"/.pyenv/bin|"$HOME"/.bun/bin|/opt/homebrew/opt/openjdk/bin)
            continue ;;
        "$HOME"/.browser-use-env/bin)
            [ "$_dev_dir" = "${VIRTUAL_ENV:-}/bin" ] || continue ;;
    esac
    case ":$_dev_path:" in
        *":$_dev_dir:"*) ;;
        *) _dev_path="${_dev_path:+$_dev_path:}$_dev_dir" ;;
    esac
done
PATH=$_dev_path
export PATH
unset _dev_path _dev_candidates _dev_dir
unset NVM_DIR NVM_BIN NVM_INC NVM_DEFAULT_BIN PYENV_ROOT PYENV_VERSION BUN_INSTALL
export PNPM_HOME="$HOME/Library/pnpm"
export JAVA_HOME="$HOME/.local/share/mise/installs/java/global"
export HYPERFRAMES_PYTHON="$HOME/.venvs/hyperframes-kokoro/bin/python"
export BASH_ENV="$HOME/.config/dev-machine/shell/env.sh"
if [ -r "$HOME/.config/dev-machine/private/env.sh" ]; then
    . "$HOME/.config/dev-machine/private/env.sh"
fi
