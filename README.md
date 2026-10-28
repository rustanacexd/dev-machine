# Development machine configuration

This repository owns the shell setup and tool manifests for this Mac. It keeps Python under uv, Node/Go/Java under mise, Rust under rustup, and general utilities under Homebrew. OrbStack is the active container engine.

| Command | Machine default |
| --- | --- |
| python, python3 | uv Python 3.14.9 |
| node | mise Node 22.22.0 |
| bun | mise Bun 1.3.10 |
| go | mise Go 1.26.2 |
| java | mise OpenJDK 25.0.2 |
| rustc, cargo | Existing rustup installation |
| docker | OrbStack |

Python 3.9, 3.10, 3.12, and 3.13 remain available through uv for existing environments and tools. A directory with its own mise configuration can select another language version. An explicitly activated virtual environment keeps precedence over the machine default.

The default `python`, `python3`, and `pip` use the shared environment at `~/.venvs/default`, built with uv Python 3.14.9. `python-libraries.txt` records the libraries restored from the earlier global Python installations. The Node `playwright` command takes precedence over the Python command with the same name. Use `python -m playwright` for Python Playwright. Both are installed with version 1.64.1. The separate `playwright-cli` command remains available.

`shell/env.sh` sets the shared paths for zsh, Bash, and future GUI launches. `shell/interactive.zsh` retains the existing prompt, aliases, and plugins. The startup files in the home directory are short pointers into this repository. `mise.toml`, `uv.toml`, `python-version`, and `npmrc` are linked into their tools' normal configuration locations.

`Brewfile` records Homebrew packages and Cargo-installed utilities. `python-tools.json` records Python CLI versions and interpreters, with full package constraints under `constraints/`. `npm-packages.json` records the global npm packages, including the complete Playwright test package. npm's global prefix is `~/.local/share/dev-machine/npm`, separate from Node installations. `go-tools.json` records the existing Go utility under `~/go/bin`. `shell-repositories.json` records the shell framework and plugins for a fresh restore. `local-python-projects.json` records optional local application checkouts installed into the shared Python environment.

Run the ownership check with:

```sh
python3 ~/.config/dev-machine/verify.py --expect-managed
```

Run `./bootstrap.sh` to reapply the configuration and GUI launch environment. Running it again without changes does nothing. It saves any replaced configuration before writing. Run `./bootstrap.sh --install` to install the recorded packages and missing shell plugins first. The install mode requires an existing native Homebrew installation, uv, and rustup. It preserves existing shell checkouts. Homebrew packages can resolve to newer available releases on a new machine; this is a package manifest, not an exact macOS image. The named mise, Python, and npm versions remain explicit.

Keep `private/` out of Git. It contains the preserved credential assignment used by the previous shell setup, has restricted filesystem permissions, and is ignored. Supply credentials separately when restoring onto another Mac. Do not copy credential values into this README or package manifests.

The initial migration backup is `~/.local/state/dev-machine/backups/20261028T145447Z`. It includes original startup files, package inventories, Python tool constraints, archived legacy runtimes, and the original shared agno environment configuration. See `RESTORE.md` before reverting anything.

Existing projects still use Homebrew Python 3.12 and Python.org 3.11. Those interpreters remain installed. Homebrew Python 3.13 and 3.14, Homebrew Node, and Podman remain because installed Homebrew packages need them. Their presence does not select them as the user-facing defaults.

Fourteen older nvm runtime directories and the old pyenv and pipx data are archived. The old nvm Node 22.22.0 directory remains for processes that were already running during the migration. Docker Desktop stays dormant because root-owned command links still point into its application bundle. Its data and the stopped OrbStack Postgres container are preserved. The inactive Python.org 3.12 framework is also left in its protected installation location.

New GUI launches have the managed PATH and Java location. Restart an editor or terminal that was already open to refresh its inherited environment. The migration did not quit user applications or restart container workloads.
