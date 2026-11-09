#!/usr/bin/env python3
"""Preview the saved model output; --starter explicitly opens the broken task input."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
TASK = ROOT / 'field-desk-locale-rollout'
STARTER = TASK / 'environment/seed/app'


def materialize_model(destination):
    evidence = TASK / 'evidence/codex'
    patch = evidence / 'model.patch'
    expected = json.loads((evidence / 'origin.json').read_text())['file_sha256']['model.patch']
    if hashlib.sha256(patch.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Saved model patch differs from its recorded evidence hash.')
    shutil.copytree(STARTER, destination)
    subprocess.run(['git', 'apply', str(patch)], cwd=destination, check=True)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--starter', action='store_true', help='Open the intentionally incomplete starter instead.')
    parser.add_argument('--port', type=int)
    parser.add_argument('--data', type=Path)
    args = parser.parse_args()
    mode = 'starter' if args.starter else 'model'
    port = args.port if args.port is not None else (8000 if args.starter else 8001)
    data = args.data or ROOT / 'validation/preview' / mode
    with tempfile.TemporaryDirectory(prefix='field-desk-preview-') as temp:
        source = STARTER if args.starter else materialize_model(Path(temp) / 'app')
        label = 'INCOMPLETE STARTER' if args.starter else 'SAVED MODEL OUTPUT (codex-02)'
        print(f'{label}: http://127.0.0.1:{port}/', flush=True)
        print(f'Starter and model use separate preview databases: {data}', flush=True)
        sys.argv = [str(source / 'serve.py'), '--port', str(port), '--data', str(data)]
        try:
            runpy.run_path(str(source / 'serve.py'), run_name='__main__')
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
