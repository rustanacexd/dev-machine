import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--output')
parser.add_argument('--expect-managed', action='store_true')
args = parser.parse_args()
home = str(Path.home())
probe = '''
set -e
for tool in python python3 node npm pnpm bun go java rustc cargo docker uv mise; do
  resolved=$(command -v "$tool" 2>/dev/null) || resolved=missing
  printf '%s=%s\\n' "$tool" "$resolved"
done
python3 -c 'import os,sys; print("python_executable=" + os.path.realpath(sys.executable)); print("python_version=" + sys.version.split()[0])'
node --version
go version
java -version
bun --version
rustc --version
cargo --version
docker --version
printf 'path=%s\\n' "$PATH"
'''
base_env = {'HOME': home, 'USER': Path.home().name, 'LOGNAME': Path.home().name,
            'SHELL': '/bin/zsh', 'PATH': '/usr/bin:/bin:/usr/sbin:/sbin',
            'TERM': 'dumb', 'LC_ALL': 'en_US.UTF-8'}
results = {}
for name, shell, flags in [
    ('zsh_noninteractive', '/bin/zsh', '-c'),
    ('zsh_login', '/bin/zsh', '-lc'),
    ('zsh_interactive', '/bin/zsh', '-ic'),
    ('zsh_login_interactive', '/bin/zsh', '-lic'),
    ('bash_login', '/bin/bash', '-lc'),
    ('bash_interactive', '/bin/bash', '-ic'),
]:
    result = subprocess.run([shell, flags, probe], cwd='/tmp', env=base_env,
                            capture_output=True, text=True, timeout=60)
    results[name] = {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
if args.output:
    Path(args.output).write_text(json.dumps(results, indent=2) + '\n')
failed = []
for name, result in results.items():
    text = result['stdout']
    selected = {line.split('=', 1)[0]: line.split('=', 1)[1]
                for line in text.splitlines() if '=' in line}
    managed = (selected.get('python', '').startswith(home + '/.venvs/default/bin/')
               and selected.get('python3', '').startswith(home + '/.venvs/default/bin/')
               and '/.local/share/mise/' in selected.get('node', '')
               and '/.local/share/mise/' in selected.get('go', '')
               and '/.local/share/mise/' in selected.get('java', '')
               and '/.local/share/mise/' in selected.get('npm', '')
               and '/.local/share/mise/' in selected.get('bun', '')
               and selected.get('rustc', '').startswith(home + '/.cargo/bin/')
               and selected.get('cargo', '').startswith(home + '/.cargo/bin/')
               and selected.get('docker', '').startswith(home + '/.orbstack/bin/')
               and '/.local/share/uv/python/' in selected.get('python_executable', '')
               and result['returncode'] == 0
               and '/.nvm/' not in selected.get('path', '')
               and '/.pyenv/' not in selected.get('path', '')
               and '/.browser-use-env/' not in selected.get('path', ''))
    if args.expect_managed and not managed:
        failed.append(name)
    print(json.dumps({'shell': name, 'managed': managed, 'selected': selected}))

root = Path(__file__).resolve().parent
library_check = subprocess.run([home + '/.venvs/default/bin/python', '-c',
                               'import numpy,pandas,pyarrow,polars,bs4,docx,pypdf; from playwright.sync_api import sync_playwright'],
                              capture_output=True, text=True, timeout=60)
if args.expect_managed and library_check.returncode:
    failed.append('Shared Python libraries')
print(json.dumps({'shared_python_libraries': library_check.returncode == 0}))

playwright_check = subprocess.run([home + '/.local/share/dev-machine/npm/bin/playwright', '--version'],
                                 capture_output=True, text=True, timeout=30)
if args.expect_managed and playwright_check.returncode:
    failed.append('Node Playwright command')
print(json.dumps({'node_playwright': playwright_check.returncode == 0}))

python_tools = json.loads((root / 'python-tools.json').read_text())
for name in python_tools['tools']:
    interpreter = Path(home) / '.local/share/uv/tools' / name / 'bin/python'
    managed = '/.local/share/uv/python/' in str(interpreter.resolve())
    if args.expect_managed and not managed:
        failed.append('Python tool ' + name)
    print(json.dumps({'python_tool': name, 'managed': managed}))

context = subprocess.run([home + '/.orbstack/bin/docker', 'context', 'show'],
                         capture_output=True, text=True, timeout=15)
docker_ok = context.returncode == 0 and context.stdout.strip() == 'orbstack'
if args.expect_managed and not docker_ok:
    failed.append('Docker context')
print(json.dumps({'docker_context': context.stdout.strip(), 'managed': docker_ok}))
if failed:
    raise SystemExit('Unexpected command ownership: ' + ', '.join(failed))
