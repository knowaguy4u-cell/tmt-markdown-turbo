#!/usr/bin/env python3
"""Fresh-process, full-I/O CPU comparison. Usage: python3 tools/benchmark.py KIT"""
import hashlib
import json
import os
from pathlib import Path
import resource
import statistics
import subprocess
import sys
import tempfile
import time

kit = Path(sys.argv[1]).resolve()
root = Path(__file__).resolve().parent.parent
node = subprocess.check_output(['node', '--version'], text=True).strip()
drivers = {'baseline': kit / 'baselines/main.ts', 'entry': root / 'main.ts'}
rows = []
reference = None

def run(name, output):
    global reference
    env = dict(os.environ, MAKEFUN_INPUT_DIR=str(kit / 'practice/input'), MAKEFUN_OUTPUT_DIR=output)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    subprocess.run(['node', str(drivers[name])], env=env, check=True, capture_output=True)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    data = (Path(output) / 'html.json').read_bytes()
    if reference is None:
        reference = data
    assert data == reference, f'{name} changed output'
    return {'name': name, 'cpu_seconds': cpu, 'wall_seconds': wall}

with tempfile.TemporaryDirectory(prefix='md-benchmark-') as output:
    for name in drivers:
        run(name, output)  # One fresh-process untimed warmup per implementation.
    for pair in range(9):
        order = ['baseline', 'entry'] if pair % 2 == 0 else ['entry', 'baseline']
        for name in order:
            row = dict(pair=pair + 1, **run(name, output))
            rows.append(row)
            print(json.dumps(row), flush=True)
medians = {name: statistics.median(r['cpu_seconds'] for r in rows if r['name'] == name) for name in drivers}
report = {
    'node': node, 'method': 'RUSAGE_CHILDREN user+system; fresh node; full driver I/O; one warmup each; 9 alternating pairs',
    'runs': rows, 'median_cpu_seconds': medians,
    'speedup': medians['baseline'] / medians['entry'],
    'cpu_reduction_percent': 100 * (1 - medians['entry'] / medians['baseline']),
    'output_sha256': hashlib.sha256(reference).hexdigest(),
    'official_heat': False,
}
(root / 'evidence/benchmark.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'runs'}, indent=2))
