#!/usr/bin/env python3
"""Preview a completed model job; --starter explicitly opens the unfinished input."""
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


def model_output(job=None):
    jobs = ROOT / 'jobs' / job if job else ROOT / 'jobs'
    candidates = jobs.glob('*/result.json') if job else jobs.glob('*/*/result.json')
    for result in sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True):
        data = json.loads(result.read_text())
        app = result.parent / 'artifacts/app'
        if data.get('finished_at') and (data.get('agent_info') or {}).get('name') in ['codex','claude-code'] and (app / 'serve.py').is_file() and (app / 'static').is_dir():
            return app, result.parent.name
    raise SystemExit('No completed model output found. Finish a Harbor model job first, or use --starter.')


def recorded_output(role, destination):
    evidence = TASK / 'evidence' / role
    origin = json.loads((evidence / 'origin.json').read_text())
    shutil.copytree(TASK / 'environment/seed/app', destination)
    subprocess.run(['git', 'apply', str(evidence / 'model.patch')], cwd=destination, check=True)
    for name, digest in origin['source_files_sha256'].items():
        candidate = (destination / name).resolve()
        if not candidate.is_relative_to(destination.resolve()) or hashlib.sha256(candidate.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Recorded source differs from its evidence hash: ' + name)
    return destination, 'recorded-' + role


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument('--starter', action='store_true')
    choice.add_argument('--job', help='A completed job directory name under jobs/.')
    choice.add_argument('--recorded', choices=['claude', 'codex'], help='Preview bundled evidence without jobs/ or a model call.')
    parser.add_argument('--port', type=int)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='field-desk-preview-') as temp:
        if args.starter:
            source, name = TASK / 'environment/seed/app', 'INCOMPLETE STARTER'
        elif args.recorded:
            source, name = recorded_output(args.recorded, Path(temp) / 'app')
        else:
            source, name = model_output(args.job)
        port = args.port if args.port is not None else (8000 if args.starter else 8001)
        data = ROOT / 'validation/preview' / name
        print(f'{name}: http://127.0.0.1:{port}/', flush=True)
        sys.argv = [str(source / 'serve.py'), '--port', str(port), '--data', str(data)]
        try:
            runpy.run_path(str(source / 'serve.py'), run_name='__main__')
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
