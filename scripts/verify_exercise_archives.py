"""Extract the actual reader downloads and run their documented offline commands."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def run(folder, args, expected=0):
    environment = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    result = subprocess.run([sys.executable, *args], cwd=folder, capture_output=True, text=True, encoding='utf-8', timeout=45, env=environment)
    if result.returncode != expected:
        raise AssertionError(f'{args}: expected exit {expected}, got {result.returncode}: {result.stderr[-1200:]}')
    counts = re.findall(r'Ran (\d+) tests?', result.stdout + result.stderr)
    return {'command': 'python ' + ' '.join(args), 'exit_code': result.returncode,
            'unit_tests': sum(map(int, counts))}

def extract(archive, folder):
    with ZipFile(ROOT / archive) as package:
        for item in package.infolist():
            target = (folder / item.filename).resolve()
            assert target.is_relative_to(folder.resolve()), 'Archive path escapes extraction directory'
            assert '__pycache__' not in item.filename and not item.filename.endswith('.pyc'), 'Cache file in reader download'
        package.extractall(folder)

def main():
    results = []
    with TemporaryDirectory(prefix='bible-reader-downloads-') as temporary:
        base = Path(temporary)
        v2 = base / 'volume2'
        v2.mkdir()
        extract('examples/learning-edition/volume2-starter.zip', v2)
        for name in ['ontology_lab.py', 'sample_data.json', 'test_ontology_lab.py']:
            assert (v2 / name).read_bytes() == (ROOT / 'examples/agent-ontology' / name).read_bytes(), 'Starter differs from verified common lab'
        results.append(run(v2, ['ontology_lab.py']))
        results.append(run(v2, ['-m', 'unittest', '-v', 'test_ontology_lab.py']))
        results.append(run(v2, ['run_scenarios.py']))
        v34 = base / 'volumes34'
        v34.mkdir()
        extract('examples/claude-code-checks/reader-checks.zip', v34)
        results.append(run(v34, ['examples/claude-code-checks/reader_lab.py']))
        results.append(run(v34, ['examples/claude-code-checks/run_checks.py']))
        results.append(run(v34, ['examples/claude-code-checks/run_checks.py', '--demo-failure'], expected=1))
        v5 = base / 'volume5'
        v5.mkdir()
        extract('examples/operations-edition/operations-practice.zip', v5)
        work = v5 / 'examples/operations-edition'
        results.append(run(work, ['operations_lab.py']))
        results.append(run(work, ['-m', 'unittest', '-v', 'test_operations_lab.py']))
        kit = base / 'work-completion-kit'
        kit.mkdir()
        extract('examples/work-completion-kit/work-completion-kit.zip', kit)
        project = kit / 'examples/work-completion-kit'
        for name in ['workbench.html', 'kit-engine.js', 'project-example.js', 'project-template.js',
                     'project-example.json', 'project-template.json', 'workbook-ko.md',
                     'workbook-en.md', 'completed-example.md', 'acceptance-rubric.md']:
            assert (project / name).is_file(), f'Missing work-completion material: {name}'
        environment = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
        checked = subprocess.run(['node', str(project / 'test_kit_engine.cjs')],
                                 cwd=project, capture_output=True, text=True, encoding='utf-8',
                                 timeout=45, env=environment)
        assert checked.returncode == 0, 'Bundled work-completion tests failed: ' + checked.stdout[-2500:] + checked.stderr[-1500:]
        summary = json.loads(checked.stdout.strip().splitlines()[-1])
        kit_tests = sum(line.startswith('PASS ') for line in checked.stdout.splitlines())
        assert kit_tests > 0 and summary['passed'] == kit_tests, 'No work-completion acceptance checks were executed'
        assert summary['network'] is False and summary['browser'] is False and summary['actual_execution'] is False
    total = sum(item['unit_tests'] for item in results)
    assert total == 41, f'Expected all 41 current unit tests to run, got {total}'
    print(json.dumps({'download_commands': results, 'python_tests': total,
                      'bundled_kit_tests': kit_tests, 'network_calls': 0}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
