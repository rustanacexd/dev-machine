# Development machine configuration

This repository holds the shell setup and tool manifests for this Mac. Python is managed by uv, Node, Bun, Go and Java by mise, Rust by rustup, and general utilities by Homebrew. OrbStack provides Docker. Agents should read `AGENTS.md` first.

| Command | Machine default |
| --- | --- |
| python, python3 | uv Python 3.14.9 |
| node | mise Node 26.13.0 |
| bun | mise Bun 1.3.10 |
| go | mise Go 1.26.2 |
| java | mise OpenJDK 25.0.2 |
| rustc, cargo | rustup |
| docker | OrbStack |

Python 3.9, 3.10, 3.12 and 3.13 are also installed through uv. A directory with its own mise configuration can select another version. An activated virtual environment takes precedence over the machine default.

The default `python`, `python3` and `pip` use the shared environment at `~/.venvs/default`. `python-libraries.txt` lists its libraries. The Node `playwright` command takes precedence over the Python one, so use `python -m playwright` for Python Playwright. npm's global prefix is `~/.local/share/dev-machine/npm`.

## Use

```sh
./bootstrap.sh             # reapply the shell pointers, config links and GUI environment
./bootstrap.sh --install   # install the recorded packages first
python3 verify.py --expect-managed
```

The install mode needs Homebrew, uv and rustup already installed. Homebrew packages can resolve to newer releases on a new machine. The mise, Python and npm versions are pinned.

Credentials are not in Git. Put them in `private/env.sh` or `~/.zshrc.secrets` when setting up another Mac.
