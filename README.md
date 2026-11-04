# Development machine configuration

Portable configuration for my Mac: shell, prompt, terminal and editor configs, plus manifests of every tool, so a new Mac can be rebuilt with one command. Python is managed by uv, Node, Bun, Go and Java by mise, Rust by rustup, and general utilities by Homebrew. OrbStack provides Docker. Agents should read `AGENTS.md` first.

| Command | Machine default |
| --- | --- |
| python, python3 | uv Python 3.14.9 |
| node | mise Node 26.13.0 |
| bun | mise Bun 1.3.10 |
| go | mise Go 1.26.2 |
| java | mise OpenJDK 25.0.2 |
| rustc, cargo | rustup stable |
| docker | OrbStack |

Python 3.9, 3.10, 3.12 and 3.13 are also installed through uv. A directory with its own mise configuration can select another version. An activated virtual environment takes precedence over the machine default.

The default `python`, `python3` and `pip` use the shared environment at `~/.venvs/default`. `python-libraries.txt` lists its libraries. The Node `playwright` command takes precedence over the Python one, so use `python -m playwright` for Python Playwright. npm's global prefix is `~/.local/share/dev-machine/npm`.

## Set up a new Mac

The setup assumes Apple Silicon, with Homebrew in `/opt/homebrew`.

1. Install Homebrew from https://brew.sh.
2. Clone this repository to `~/.config/dev-machine`:

   ```sh
   git clone https://github.com/rustanacexd/dev-machine.git ~/.config/dev-machine
   ```

3. Install and configure everything:

   ```sh
   ~/.config/dev-machine/bootstrap.sh --install
   ```

   This installs uv, rustup, Claude Code and Zed, the Homebrew and Cargo packages, the mise runtimes, the Python versions, tools and shared libraries, the npm and Go tools, and the oh-my-zsh plugins. It then links the configs and loads the LaunchAgents.
4. Recreate the two secret files, which are not in Git:
   - `~/.config/dev-machine/private/env.sh`, mode 600, exporting `EXA_API_KEY`.
   - `~/.zshrc.secrets`, exporting `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `GEMINI_API_KEY` and `GOOGLE_GENERATIVE_AI_API_KEY`.
5. Open OrbStack once and finish its setup. That creates `~/.orbstack/bin`, which makes `docker` use OrbStack.
6. Log out and back in, so GUI apps get the PATH and secrets, then check:

   ```sh
   python3 ~/.config/dev-machine/verify.py --expect-managed
   ```

Homebrew and Cargo packages install their newest releases. The mise runtimes, Python tools and libraries, npm and Go tools, and shell plugins are pinned.

## Installed by hand

These are on the current Mac but no manifest installs them. Install the ones you still use from their vendors.

- Apps: Amphetamine, Antigravity, ChatGPT, Claude, Cloudflare WARP, Devin, Discord, EasyCLIProxyAPI, Firefox, FocusPomo, Google Chrome, Herdr, Magnet, Notion, Open Design, OpenCode, Parallels Desktop, Power JSON Editor, Rex, Slack, Speechify, TablePlus, Tailscale, Things 3, Wispr Flow, Xcode.
- Command-line tools in `~/.local/bin` from their own installers: `cursor-agent`, `devbox`, `herdr`, `langsmith`, `plannotator`, `sentry`.

## Day to day

```sh
./bootstrap.sh                       # reapply the configs and LaunchAgents after editing this repo
python3 verify.py --expect-managed   # check which tool every shell type resolves
```
