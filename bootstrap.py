import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description='Restore the development-machine configuration.')
parser.add_argument('--install', action='store_true', help='Install the declared packages before configuring shells.')
args = parser.parse_args()
home = Path.home()
root = Path(__file__).resolve().parent
if root != home / '.config/dev-machine':
    raise SystemExit('Place this repository at ~/.config/dev-machine before running bootstrap.')

python = json.loads((root / 'python-tools.json').read_text())
if args.install:
    for repository in json.loads((root / 'shell-repositories.json').read_text()):
        destination = home / repository['path']
        if not destination.exists():
            subprocess.run(['git', 'clone', '--filter=blob:none', '--no-checkout',
                            repository['url'], str(destination)], check=True)
            subprocess.run(['git', '-C', str(destination), 'checkout', '--detach',
                            repository['revision']], check=True)
    subprocess.run(['/opt/homebrew/bin/brew', 'bundle', '--no-upgrade', '--file', str(root / 'Brewfile')], check=True)
    subprocess.run(['/opt/homebrew/bin/mise', 'install'], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/uv', 'python', 'install', *python['installed']], check=True)
    subprocess.run(['/opt/homebrew/bin/uv', 'python', 'install', python['default'], '--default'], check=True)
    shared_environment = home / '.venvs/default'
    if not (shared_environment / 'pyvenv.cfg').exists():
        subprocess.run(['/opt/homebrew/bin/uv', 'venv', '--seed', str(shared_environment),
                        '--python', python['default']], check=True)
    subprocess.run(['/opt/homebrew/bin/uv', 'pip', 'install', '--python',
                    str(shared_environment / 'bin/python'), '--requirement',
                    str(root / 'python-libraries.txt')], check=True)
    for relative in json.loads((root / 'local-python-projects.json').read_text()):
        project = home / relative
        if project.exists():
            subprocess.run(['/opt/homebrew/bin/uv', 'pip', 'install', '--no-deps', '--python',
                            str(shared_environment / 'bin/python'), str(project)], check=True)
        else:
            print('Local Python project is not present; skipped: ' + relative)
    for name, tool in python['tools'].items():
        command = ['/opt/homebrew/bin/uv', 'tool', 'install', '--managed-python', '--python', tool['python'],
                   '--constraints', str(root / 'constraints' / (name + '.txt')),
                   name + '==' + tool['version']]
        for extra in tool.get('with', []):
            command.extend(['--with', extra])
        subprocess.run(command, check=True)
    packages = json.loads((root / 'npm-packages.json').read_text())
    subprocess.run(['/opt/homebrew/bin/mise', 'exec', '--', 'npm', 'install', '--global', '--prefix',
                    str(home / '.local/share/dev-machine/npm'),
                    *[name + '@' + version for name, version in packages.items()]], cwd=root, check=True)
    subprocess.run(['/opt/homebrew/bin/mise', 'exec', '--',
                    str(home / '.local/share/dev-machine/npm/bin/playwright'),
                    'install', 'chromium'], cwd=root, check=True)
    go_tools = json.loads((root / 'go-tools.json').read_text())
    for package in go_tools:
        subprocess.run(['/opt/homebrew/bin/mise', 'exec', '--', 'go', 'install', package],
                       cwd=root, env={**os.environ, 'GOBIN': str(home / 'go/bin')}, check=True)

stubs = {
    '.zshenv': '. "$HOME/.config/dev-machine/shell/env.sh"\n',
    '.zprofile': '. "$HOME/.config/dev-machine/shell/login.zsh"\n',
    '.zshrc': '. "$HOME/.config/dev-machine/shell/interactive.zsh"\n',
    '.profile': '. "$HOME/.config/dev-machine/shell/env.sh"\n',
    '.bashrc': '. "$HOME/.config/dev-machine/shell/interactive.bash"\n',
    '.bash_profile': '. "$HOME/.profile"\ncase $- in\n    *i*) . "$HOME/.bashrc" ;;\nesac\n',
    'Library/LaunchAgents/com.dev-machine.gui-env.plist':
        (root / 'launchd/com.dev-machine.gui-env.plist').read_text(),
}
links = {
    '.config/mise/config.toml': root / 'mise.toml',
    '.config/uv/uv.toml': root / 'uv.toml',
    '.config/uv/.python-version': root / 'python-version',
    '.npmrc': root / 'npmrc',
    '.vimrc': root / 'vimrc',
    '.tmux.conf': root / 'tmux.conf',
    '.config/ghostty/config': root / 'ghostty.config',
    '.config/starship.toml': root / 'starship.toml',
    'Library/Java/JavaVirtualMachines/dev-machine.jdk': home / '.local/share/mise/installs/java/global',
}
subprocess.run(['git', '-C', str(root), 'config', 'core.hooksPath', '.githooks'], check=True)
changes = []
for relative in [*stubs, *links]:
    target = home / relative
    if relative in stubs:
        desired = stubs[relative]
        if target.is_file() and not target.is_symlink() and target.read_text() == desired:
            continue
    else:
        desired = links[relative]
        if target.is_symlink() and target.resolve() == desired.resolve():
            continue
        if target.is_dir() and not target.is_symlink():
            raise SystemExit('Refusing to replace directory: ' + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.dev-machine-tmp')
    if temporary.is_symlink() or temporary.exists():
        temporary.unlink()
    if relative in stubs:
        temporary.write_text(desired)
    else:
        temporary.symlink_to(desired)
    temporary.replace(target)
    changes.append(relative)
    if relative.startswith('Library/LaunchAgents/'):
        domain = 'gui/' + str(os.getuid())
        subprocess.run(['launchctl', 'bootout', domain, str(target)], capture_output=True)
        subprocess.run(['launchctl', 'bootstrap', domain, str(target)], check=True)

environment = {'HOME': str(home), 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin'}
shell = '. "$HOME/.config/dev-machine/shell/env.sh"; printf "%s\\n" "$PATH" "$JAVA_HOME" "$BASH_ENV"'
values = subprocess.check_output(['/bin/sh', '-c', shell], env=environment, text=True).splitlines()
gui_updated = []
for name, value in zip(['PATH', 'JAVA_HOME', 'BASH_ENV'], values, strict=True):
    old = subprocess.run(['launchctl', 'getenv', name], capture_output=True, text=True)
    previous = old.stdout.rstrip('\n') if old.returncode == 0 else None
    if previous == value:
        continue
    gui_updated.append(name)
    subprocess.run(['launchctl', 'setenv', name, value], check=True)
print(json.dumps({'configured': changes, 'gui_updated': gui_updated}, indent=2))
