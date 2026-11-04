# Agent guide

This repository is the shell and toolchain configuration for this Mac. It must live at `~/.config/dev-machine`. Every shell on the machine loads it, so a mistake here breaks every terminal, script and agent. Read this file before you edit anything.

## Where things are

The files in the home directory are one-line pointers. Edit the files they load instead of the pointers.

| Home file | Loads | Runs for |
| --- | --- | --- |
| `~/.zshenv` | `shell/env.sh` | every zsh, including `zsh -c` |
| `~/.zprofile` | `shell/login.zsh` | zsh login shells, after macOS `path_helper` |
| `~/.zshrc` | `shell/interactive.zsh` | interactive zsh |
| `~/.profile`, `~/.bash_profile`, `~/.bashrc` | `shell/env.sh`, `shell/interactive.bash` | bash |

- `shell/env.sh` builds PATH and the shared environment. It also runs for every non-interactive bash script through `BASH_ENV`.
- `shell/interactive.zsh` holds the completion setup, the oh-my-zsh libraries and plugins, the tool hooks, and the aliases.
- `mise.toml`, `uv.toml`, `python-version` and `npmrc` are linked into their tools' normal config locations by `bootstrap.py`.
- `launchd/com.dev-machine.gui-env.plist` sets `EXA_API_KEY` for GUI apps at login.
- The starship prompt config is not here. `~/.config/starship.toml` links to `~/code/dotfiles/starship.toml`, a separate repository.
- The manifests (`Brewfile`, `python-tools.json`, `constraints/`, `npm-packages.json`, `go-tools.json`, `python-libraries.txt`, `local-python-projects.json`, `shell-repositories.json`) feed `bootstrap.sh --install`.

## Secrets

Never commit a secret, and never print one in output.

- `private/env.sh` holds `EXA_API_KEY`. It is git-ignored and has mode 600.
- `~/.zshrc.secrets` holds the AWS and Gemini keys. It is outside the repository, and `interactive.zsh` sources it.

Put any new credential in one of those two files. Keep `.gitignore` covering them.

## Startup speed rules

A login shell starts in about 45 ms. Keep it that way.

- Don't add `eval "$(tool init zsh)"`. Use `_cached_init tool init zsh` in `interactive.zsh`. It caches the output in `~/.cache/zsh` under the binary's resolved path, so it regenerates when the tool is upgraded. Put the call above the `unfunction _cached_init` line.
- Don't add `mise activate` to zsh. Tools resolve through the mise shims that `env.sh` puts on PATH.
- Don't source `oh-my-zsh.sh`. `interactive.zsh` loads the oh-my-zsh lib files and the plugins in `plugins=(...)` directly. To add a plugin, clone it into `~/.oh-my-zsh/custom/plugins/`, add it to `plugins`, and record it in `shell-repositories.json`.
- Add completion directories to the `fpath=(...)` line before `compinit`. A directory added after `compinit` never loads. The completion dump in `~/.cache/zsh` rebuilds when `fpath` changes or the dump is a day old.
- Keep `env.sh` free of subprocesses such as `launchctl`, `brew --prefix` or `$(...)`, because it runs for every shell and every bash script. Source `env.sh` at most once per startup file.

## Check a change

Start a new shell for every check, because a running shell keeps the old config.

```sh
python3 ~/.config/dev-machine/verify.py --expect-managed   # tool ownership in every shell type
zsh -il -c 'print ok'                                      # loads without errors
hyperfine -N -w 3 'zsh -il -c exit'                        # startup time, ~45 ms
```

`./bootstrap.sh` reapplies the home pointers, the config links, the LaunchAgent and the GUI environment. Running it again changes nothing. `./bootstrap.sh --install` first installs everything in the manifests.
