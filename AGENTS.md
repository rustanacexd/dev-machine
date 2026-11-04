# Agent guide

This repository is the portable configuration for this Mac. Its job is to rebuild the same setup on a new Mac with one command, so anything installed or configured by hand that is not recorded here is lost on the next machine. It must live at `~/.config/dev-machine`. Every shell on the machine loads it, so a mistake here breaks every terminal, script and agent. Read this file before you edit anything.

## Set up a new Mac

Follow these steps when the user asks you to set up a Mac from this repository. The setup assumes Apple Silicon and macOS with an admin user. The full run takes about 15 to 30 minutes, mostly compiling Cargo tools.

1. If `/opt/homebrew/bin/brew` is missing, ask the user to install Homebrew themselves in a terminal: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`. It needs their password, and it installs the Xcode Command Line Tools, which provide `git`.
2. Clone the repository to the required path: `git clone https://github.com/rustanacexd/dev-machine.git ~/.config/dev-machine`. If `~/.config/dev-machine` already exists, run `git -C ~/.config/dev-machine pull` instead.
3. Run `~/.config/dev-machine/bootstrap.sh --install` in a terminal the user can see, because it stops once for their password while Homebrew installs `karabiner-elements`. You can't type the password, so tell the user before you start. The script stops on the first failure. Fix the cause, then rerun the same command; a rerun skips everything that is already installed.
4. Ask the user for the secret values and write the two secret files. Never print the values or commit them.
   - `~/.config/dev-machine/private/env.sh` with mode 600: `export EXA_API_KEY=...`
   - `~/.zshrc.secrets`: `export AWS_ACCESS_KEY_ID=...`, `AWS_SECRET_ACCESS_KEY`, `GEMINI_API_KEY`, `GOOGLE_GENERATIVE_AI_API_KEY`
5. Ask the user to do the steps that need the GUI. Wait until they confirm.
   - Open OrbStack once and finish its setup. That creates `~/.orbstack/bin` and the `orbstack` Docker context.
   - Open Karabiner-Elements and allow the permissions macOS asks for.
   - Log out and back in, so GUI apps get the PATH and secrets from the `com.dev-machine.gui-env` LaunchAgent.
6. Open a new shell and run `python3 ~/.config/dev-machine/verify.py --expect-managed`. It must exit 0. Each output line names the shell or tool it checked. Fix any line with `"managed": false` before you report success.
7. Tell the user what README.md lists under "Installed by hand". Those apps and tools are not in any manifest, so the user must install the ones they still use.

## Keep it reproducible

When you install a tool or change a setting, record it in the matching manifest in the same change.

| Installed with | Record it in |
| --- | --- |
| `brew install`, `brew install --cask`, `cargo install` | `Brewfile` |
| `npm install -g` | `npm-packages.json`, with the exact version |
| `uv tool install` | `python-tools.json` and `constraints/<tool>.txt` (`uv pip freeze --python ~/.local/share/uv/tools/<tool>/bin/python`) |
| `uv pip install` into `~/.venvs/default` | `python-libraries.txt` |
| `go install` | `go-tools.json`, with the version |
| a vendor `curl ... \| sh` installer | the `installers` table in `bootstrap.py`, keyed by the path it creates |
| a language runtime | `mise.toml` |
| an oh-my-zsh plugin | `shell-repositories.json`, with the commit |
| a LaunchAgent | a plist in `launchd/`; `bootstrap.py` installs every file there |

Use `$HOME`, never `/Users/<name>`, in anything committed. Check for drift with `brew bundle cleanup --file=Brewfile`, which lists installed packages the Brewfile lacks without removing them unless you pass `--force`.

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
- `bootstrap.py` links these files into their tools' normal locations. Edit the copy here; the live path is a symlink.

  | File | Live path |
  | --- | --- |
  | `mise.toml` | `~/.config/mise/config.toml` |
  | `uv.toml`, `python-version` | `~/.config/uv/` |
  | `npmrc` | `~/.npmrc` |
  | `starship.toml` | `~/.config/starship.toml` |
  | `ghostty.config` | `~/.config/ghostty/config` |
  | `tmux.conf` | `~/.tmux.conf` |
  | `vimrc` | `~/.vimrc` |

  To track another config, add it to the `links` table in `bootstrap.py` and run `./bootstrap.sh`.
- `launchd/com.dev-machine.gui-env.plist` gives GUI apps `PATH`, `JAVA_HOME`, `BASH_ENV` and `EXA_API_KEY` from `env.sh` at every login.
- `launchd/com.dev-machine.right-command-to-control.plist` remaps the right Command key to Control at login.
- The manifests (`Brewfile`, `python-tools.json`, `constraints/`, `npm-packages.json`, `go-tools.json`, `python-libraries.txt`, `local-python-projects.json`, `shell-repositories.json`) feed `bootstrap.sh --install`.

## Secrets

Never commit a secret, and never print one in output.

- `private/env.sh` exports `EXA_API_KEY`. It is git-ignored and has mode 600. `env.sh` sources it, so every shell and GUI app gets it.
- `~/.zshrc.secrets` exports `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `GEMINI_API_KEY` and `GOOGLE_GENERATIVE_AI_API_KEY`. It is outside the repository, and `interactive.zsh` sources it.

On a new Mac, both files must be recreated by hand.

Put any new credential in one of those two files. Keep `.gitignore` covering them. The `.githooks/pre-commit` hook runs `trufflehog` on the staged files and blocks a commit that looks like it contains a credential. `bootstrap.py` turns the hook on with `core.hooksPath`. Don't bypass it with `--no-verify`.

## Startup speed rules

A login shell starts in about 45 ms. Keep it that way.

- Don't add `eval "$(tool init zsh)"`. Use `_cached_init tool init zsh` in `interactive.zsh`. It caches the output in `~/.cache/zsh` under the binary's resolved path, so it regenerates when the tool is upgraded. Put the call above the `unfunction _cached_init` line.
- Don't add `mise activate` to zsh or bash. Tools resolve through the mise shims that `env.sh` puts on PATH.
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

For prompt, terminal or editor configs, check them with `starship prompt`, `ghostty +validate-config`, `tmux source-file ~/.tmux.conf` or `vim -Nu ~/.vimrc -es -c 'qa!'`.

`./bootstrap.sh` reapplies the home pointers, the config links, the git hook and the LaunchAgents. It overwrites what it replaces and keeps no backup copies. Running it again changes nothing. `./bootstrap.sh --install` first installs everything in the manifests and the `installers` table. It needs only Homebrew; `bootstrap.sh` installs uv itself.
