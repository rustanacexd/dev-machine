import argparse
import json
import os
from pathlib import Path
import subprocess
import tomllib

parser = argparse.ArgumentParser(description='Restore the development-machine configuration.')
parser.add_argument('--install', action='store_true', help='Install the declared packages before configuring shells.')
args = parser.parse_args()
home = Path.home()
root = Path(__file__).resolve().parent
if root != home / '.config/dev-machine':
    raise SystemExit('Place this repository at ~/.config/dev-machine before running bootstrap.')

brew = '/opt/homebrew/bin/brew'
mise = '/opt/homebrew/bin/mise'
uv = '/opt/homebrew/bin/uv'
python = json.loads((root / 'python-tools.json').read_text())
java = tomllib.loads((root / 'mise.toml').read_text())['tools']['java']
os.environ['PATH'] = os.pathsep.join([str(home / '.cargo/bin'), str(home / '.local/bin'),
                                      '/opt/homebrew/bin', os.environ['PATH']])

if args.install:
    installers = {
        home / '.cargo/bin/rustup':
            'curl --proto =https --tlsv1.2 -fsSL https://sh.rustup.rs | sh -s -- -y --no-modify-path',
        home / '.local/bin/claude': 'curl -fsSL https://claude.ai/install.sh | bash',
        Path('/Applications/Zed.app'): 'curl -fsSL https://zed.dev/install.sh | sh',
    }
    for installed, command in installers.items():
        if not installed.exists():
            subprocess.run(['/bin/sh', '-c', command], check=True)
    for repository in json.loads((root / 'shell-repositories.json').read_text()):
        destination = home / repository['path']
        if not destination.exists():
            subprocess.run(['git', 'clone', '--filter=blob:none', '--no-checkout',
                            repository['url'], str(destination)], check=True)
            subprocess.run(['git', '-C', str(destination), 'checkout', '--detach',
                            repository['revision']], check=True)
    subprocess.run([brew, 'bundle', '--no-upgrade', '--file', str(root / 'Brewfile')], check=True)
    subprocess.run([mise, 'trust', str(root / 'mise.toml')], check=True)
    subprocess.run([mise, 'install'], cwd=root, check=True)
    subprocess.run([uv, 'python', 'install', *python['installed']], check=True)
    subprocess.run([uv, 'python', 'install', python['default'], '--default'], check=True)
    shared_environment = home / '.venvs/default'
    if not (shared_environment / 'pyvenv.cfg').exists():
        subprocess.run([uv, 'venv', '--seed', str(shared_environment),
                        '--python', python['default']], check=True)
    subprocess.run([uv, 'pip', 'install', '--python',
                    str(shared_environment / 'bin/python'), '--requirement',
                    str(root / 'python-libraries.txt')], check=True)
    for relative in json.loads((root / 'local-python-projects.json').read_text()):
        project = home / relative
        if project.exists():
            subprocess.run([uv, 'pip', 'install', '--no-deps', '--python',
                            str(shared_environment / 'bin/python'), str(project)], check=True)
        else:
            print('Local Python project is not present; skipped: ' + relative)
    for name, tool in python['tools'].items():
        command = [uv, 'tool', 'install', '--managed-python', '--python', tool['python'],
                   '--constraints', str(root / 'constraints' / (name + '.txt')),
                   name + '==' + tool['version']]
        for extra in tool.get('with', []):
            command.extend(['--with', extra])
        subprocess.run(command, check=True)
    packages = json.loads((root / 'npm-packages.json').read_text())
    subprocess.run([mise, 'exec', '--', 'npm', 'install', '--global', '--prefix',
                    str(home / '.local/share/dev-machine/npm'),
                    *[name + '@' + version for name, version in packages.items()]], cwd=root, check=True)
    subprocess.run([mise, 'exec', '--',
                    str(home / '.local/share/dev-machine/npm/bin/playwright'),
                    'install', 'chromium'], cwd=root, check=True)
    go_tools = json.loads((root / 'go-tools.json').read_text())
    for package in go_tools:
        subprocess.run([mise, 'exec', '--', 'go', 'install', package],
                       cwd=root, env={**os.environ, 'GOBIN': str(home / 'go/bin')}, check=True)

stubs = {
    '.zshenv': '. "$HOME/.config/dev-machine/shell/env.sh"\n',
    '.zprofile': '. "$HOME/.config/dev-machine/shell/login.zsh"\n',
    '.zshrc': '. "$HOME/.config/dev-machine/shell/interactive.zsh"\n',
    '.profile': '. "$HOME/.config/dev-machine/shell/env.sh"\n',
    '.bashrc': '. "$HOME/.config/dev-machine/shell/interactive.bash"\n',
    '.bash_profile': '. "$HOME/.profile"\ncase $- in\n    *i*) . "$HOME/.bashrc" ;;\nesac\n',
}
agents = sorted((root / 'launchd').glob('*.plist'))
for plist in agents:
    stubs['Library/LaunchAgents/' + plist.name] = plist.read_text()
links = {
    '.config/mise/config.toml': root / 'mise.toml',
    '.config/uv/uv.toml': root / 'uv.toml',
    '.config/uv/.python-version': root / 'python-version',
    '.npmrc': root / 'npmrc',
    '.vimrc': root / 'vimrc',
    '.tmux.conf': root / 'tmux.conf',
    '.config/ghostty/config': root / 'ghostty.config',
    '.config/starship.toml': root / 'starship.toml',
    '.local/share/mise/installs/java/global': home / '.local/share/mise/installs/java' / java,
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

# Reload every agent so the GUI environment picks up env.sh edits made since login.
domain = 'gui/' + str(os.getuid())
for plist in agents:
    installed = home / 'Library/LaunchAgents' / plist.name
    subprocess.run(['launchctl', 'bootout', domain, str(installed)], capture_output=True)
    subprocess.run(['launchctl', 'bootstrap', domain, str(installed)], check=True)
print(json.dumps({'configured': changes, 'agents': [plist.stem for plist in agents]}, indent=2))
