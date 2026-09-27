#!/usr/bin/env python3
"""Decode staging/*.jpg.b64 into root *.jpg and commit if changed."""
import base64, pathlib, subprocess, os

root = pathlib.Path('.')
staging = root / 'staging'
changed = []
for b64path in sorted(staging.glob('*.jpg.b64')):
    name = b64path.name[:-4]  # strip .b64 -> foo.jpg
    out = root / name
    data = base64.b64decode(b64path.read_text().strip())
    if not data.startswith(b'\xff\xd8'):
        raise SystemExit(f'not a jpeg after decode: {b64path}')
    if out.exists() and out.read_bytes() == data:
        continue
    out.write_bytes(data)
    changed.append(str(out))
    print(f'wrote {out} ({len(data)} bytes)')

if not changed:
    print('no changes')
    raise SystemExit(0)

subprocess.check_call(['git', 'config', 'user.name', 'inimitato-buffer-bot'])
subprocess.check_call(['git', 'config', 'user.email', 'bot@inimitato.local'])
subprocess.check_call(['git', 'add', '--'] + changed)
subprocess.check_call(['git', 'commit', '-m', 'Decode staged Buffer stills to JPEG'])
# push with token from Actions
subprocess.check_call(['git', 'push'])
print('pushed', changed)
