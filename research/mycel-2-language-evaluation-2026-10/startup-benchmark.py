"""Warm/cache-uncontrolled local startup comparison; no application dispatch.

The frozen Sept 23 implementation and current deprecated checkout differ.
This measures installed packaging choices, not a controlled language or
same-revision extraction delta. Help prints and exits before dispatch.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import time

OUT = Path('/tmp/mycel-language-startup')
SOURCE = Path('/Users/example/repos/sylvan-stack/mycel_deprecated_v1')
PYTHON = str(SOURCE / '.venv/bin/python3.12')
NODE = '/Users/example/.nvm/versions/node/v24.21.0/bin/node'
BUNDLE = '/Users/example/bin/mycel'
ENV = {
    'PATH': '/usr/bin:/bin:/opt/homebrew/bin',
    'LANG': 'en_US.UTF-8',
    'LC_ALL': 'en_US.UTF-8',
    'PYTHONDONTWRITEBYTECODE': '1',
    'MYCEL_CONFIG': str(OUT / 'nonexistent-config.toml'),
    'TMPDIR': str(OUT / 'runtime-tmp'),
}
Path(ENV['TMPDIR']).mkdir(exist_ok=True)
assert not Path(ENV['MYCEL_CONFIG']).exists()

TARGETS = {
    'packaged_v1_help': {'argv': [BUNDLE, '--help'], 'env': ENV},
    'unbundled_v1_help': {
        'argv': [PYTHON, '-B', str(SOURCE / '.venv/bin/mycel'), '--help'],
        'env': {**ENV, 'PYTHONPATH': str(SOURCE)},
    },
    'python_interpreter_only': {'argv': [PYTHON, '-B', '-c', 'pass'], 'env': ENV},
    'node_interpreter_only': {'argv': [NODE, '-e', ''], 'env': ENV},
}
REPEATS = 20
WARMUPS = 2
SEED = 20261007
rng = random.Random(SEED)

def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def run_target(name, phase, round_id):
    target = TARGETS[name]
    started = utc_now()
    start = time.perf_counter_ns()
    process = subprocess.run(target['argv'], env=target['env'], cwd=OUT,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, timeout=25)
    elapsed = (time.perf_counter_ns() - start) / 1_000_000
    record = {'target': name, 'phase': phase, 'round': round_id,
              'started_utc': started, 'elapsed_ms': elapsed,
              'returncode': process.returncode,
              'stderr_bytes': len(process.stderr)}
    if process.returncode or process.stderr:
        record['stderr'] = process.stderr.decode('utf-8', errors='replace')[:2000]
    if process.returncode:
        raise RuntimeError(record)
    return record

def version(argv, env):
    process = subprocess.run(argv, env=env, cwd=OUT, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25,
                             check=True, text=True)
    return (process.stdout.strip() or process.stderr.strip())

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

metadata = {
    'started_utc': utc_now(), 'host': platform.platform(),
    'architecture': platform.machine(), 'seed': SEED, 'repeats': REPEATS,
    'warmups_per_target': WARMUPS, 'timing': 'parent perf_counter_ns around subprocess.run',
    'percentile_method': 'nearest rank: sorted[ceil(0.95*n)-1]',
    'order': 'each round randomly reverses packaged/unbundled pair; baselines follow in random order',
    'versions': {
        'python': version([PYTHON, '--version'], ENV),
        'node': version([NODE, '--version'], ENV),
        'packaged_mycel': version([BUNDLE, '--version'], ENV),
        'unbundled_mycel': version([PYTHON, '-B', str(SOURCE / '.venv/bin/mycel'), '--version'],
                                  TARGETS['unbundled_v1_help']['env']),
    },
    'artifacts': {
        BUNDLE: {'size_bytes': Path(BUNDLE).stat().st_size, 'sha256': digest(BUNDLE),
                 'mtime_utc': dt.datetime.fromtimestamp(Path(BUNDLE).stat().st_mtime, dt.timezone.utc).isoformat()},
        **{str(SOURCE / relative): {'sha256': digest(SOURCE / relative)}
           for relative in ['mycel/cli.py', 'mycel/config.py', 'mycel/database.py',
                            'mycel/__init__.py', 'mycel.spec', 'pyproject.toml']},
    },
    'source_git_head': subprocess.run(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'],
                                     capture_output=True, text=True, check=True).stdout.strip(),
    'source_import_path': version([PYTHON, '-B', '-c',
                                  'import mycel; print(mycel.__file__)'],
                                  TARGETS['unbundled_v1_help']['env']),
    'targets': {name: value['argv'] for name, value in TARGETS.items()},
    'sanitized_environment': ENV,
    'limits': [
        'filesystem/page caches were not flushed; all reported trials follow two warmups',
        'wall clock includes subprocess creation, scheduling, application imports, output, and process teardown',
        'packaged binary built Sept 23 and current v1 checkout have differing code; version 0.1.0 alone does not establish identical revision',
        'no real query, corpus scan, PostgreSQL, embedding service, or TypeScript application was exercised',
        'interpreter-only comparison is not evidence of application performance',
        'MYCEL_CONFIG points to nonexistent file; no owner configuration or private DB reference is read',
        'Python bytecode writes disabled; frozen executable may extract bundled files into private temporary directory',
    ],
}

records = []
for round_id in range(WARMUPS):
    names = list(TARGETS)
    rng.shuffle(names)
    for name in names:
        records.append(run_target(name, 'warmup', round_id))
print('Warmups complete', flush=True)

for round_id in range(REPEATS):
    pair = ['packaged_v1_help', 'unbundled_v1_help']
    rng.shuffle(pair)
    baseline = ['python_interpreter_only', 'node_interpreter_only']
    rng.shuffle(baseline)
    for name in pair + baseline:
        records.append(run_target(name, 'measurement', round_id))
    if (round_id + 1) % 5 == 0:
        print(f'Completed {round_id + 1}/{REPEATS} measurement rounds', flush=True)

summary = {}
for name in TARGETS:
    times = sorted(r['elapsed_ms'] for r in records
                   if r['target'] == name and r['phase'] == 'measurement')
    summary[name] = {'n': len(times), 'median_ms': statistics.median(times),
                     'p95_ms': times[math.ceil(0.95 * len(times))-1],
                     'min_ms': min(times), 'max_ms': max(times),
                     'mean_ms': statistics.mean(times)}
metadata['finished_utc'] = utc_now()
result = {'metadata': metadata, 'summary': summary, 'records': records}
(OUT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'versions': metadata['versions'], 'summary': summary,
                  'results': str(OUT / 'results.json')}, indent=2), flush=True)
