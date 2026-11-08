"""Install an integrity-pinned official Codex binary; no login/credentials here."""
import base64
import hashlib
import os
from pathlib import Path
import platform
import tarfile
import time
import urllib.request

VERSION='0.167.0'
PACKAGES={
    'aarch64':('arm64','5cv+sybRWqpRJL6KCv3YSnIx1GHRmjek997C38n1Zfno4HomKDLkNSjWLDOOc2+ISlVNSRRnySWq4zKmzlY12g=='),
    'x86_64':('x64','FNc7danfUng9Sp6w+Fh7kofNHHZpA6VMyNKWsWrS3OwHly69gywTWeiuwrUPXpJSho8Df4xqRsHfHRPzj7zYQg=='),
}
architecture,integrity=PACKAGES[platform.machine()]
url=f'https://registry.npmjs.org/@openai/codex/-/codex-{VERSION}-linux-{architecture}.tgz'
archive=Path('/tmp/codex-runtime.tgz')
for attempt in range(4):
    try:
        digest=hashlib.sha512()
        with urllib.request.urlopen(url,timeout=120) as response,archive.open('wb') as output:
            while chunk:=response.read(1024*1024):output.write(chunk);digest.update(chunk)
        if digest.digest()!=base64.b64decode(integrity):raise RuntimeError('Codex package integrity mismatch')
        break
    except Exception:
        if attempt==3:raise
        time.sleep(3)
destination=Path('/opt/codex');destination.mkdir(exist_ok=True)
with tarfile.open(archive) as package:package.extractall(destination,filter='data')
binaries=[path for path in destination.rglob('codex') if path.is_file()]
preferred=[path for path in binaries if 'linux-gnu' in str(path)] or [path for path in binaries if 'linux-musl' in str(path)] or binaries
if len(preferred)!=1:raise RuntimeError('Cannot select native Codex binary: '+str([str(path) for path in binaries]))
preferred[0].chmod(0o755)
os.symlink(preferred[0],'/usr/local/bin/codex')
archive.unlink()
print(f'Installed integrity-verified Codex {VERSION} for {architecture}')
