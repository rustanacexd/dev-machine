# Restore the previous setup

The original snapshot is `~/.local/state/dev-machine/backups/20261028T145447Z`. Its `manifest.json` identifies which configuration files existed and where their copies are stored. The directory is private because some originals contain credentials.

Restoring configuration and restoring removed packages are separate operations. Do not restore the old startup files until the old commands they reference are available again.

1. Consult `brew-formulae.txt` and `brew-inventory.txt` in the snapshot. The migration removed pyenv, pyenv-virtualenv, nvm, pipx, colima, lima, go, and openjdk. Reinstall the packages whose old behavior you need. A normal Homebrew installation selects currently available versions, which may differ from the snapshot.
2. Move the archived `.pyenv` and `.local-pipx` directories from `retired/` back to their original paths. Move any needed directory in `retired/nvm-versions/` back under `~/.nvm/versions/node/`. Preserve a newer directory instead of overwriting it silently.
3. Restore the original startup files from `files/` according to `manifest.json`. Remove a new startup file only if the manifest says the original did not exist and the current file is still the generated pointer. `.bash_profile` was newly created by this migration.
4. The original machine had no user uv configuration or global uv pin. Remove the generated links at `~/.config/uv/uv.toml` and `~/.config/uv/.python-version` only if they still point into this repository. The new `~/.npmrc` also points here. Remove it only if reverting the stable npm prefix.
5. The migration added `~/.local/bin/python`, `python3`, `python3.12`, and `python3.13`. Removing those uv-managed links restores the old command search behavior after the old startup files are back. Keep the uv installations themselves while environments still depend on them.
6. Restore each saved GUI environment value from `gui-environment.json` using `launchctl setenv`; use `launchctl unsetenv` for a value recorded as null. Restart the affected application to load the restored environment.

The Python CLI environments were rebuilt under uv. Their previous package constraints and receipts are in the snapshot. Recreate an old tool with its recorded Python interpreter and constraint file if necessary. The `langsmith-fetch` command originally pointed to the archived pipx environment.

The shared `~/.venvs/agno` environment was already broken before the migration because its pyenv Python was missing. The migration repaired it with uv Python 3.9.25. Its original `pyvenv.cfg` and interpreter-link values are in `agno-before/`; restoring them also restores that original fault.

The old Cargo-installed `rg` and `fd` executables and Cargo metadata are saved in `duplicate-tools/` and `cargo-metadata/`. Homebrew now provides both commands. The duplicate executables can be restored if you need their old behavior, but doing so makes them take precedence again.

This procedure preserves recovery evidence. It is not an automatic rollback of every package upgrade or application state. Container data was not moved or deleted.
