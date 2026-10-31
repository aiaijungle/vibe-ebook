"""Build deterministic offline exercise archives and a public release manifest."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EDITION = '2026-10-31-practical-v4'
READERS = ['book1.html', 'index.html', 'agent-bible.html', 'claude-code-bible.html', 'practical-bible.html']

def bundle(folder, name):
    directory = ROOT / folder
    files = sorted(p for p in directory.rglob('*') if p.is_file() and p.suffix in {'.py', '.md', '.json', '.csv', '.html', '.js', '.cjs'} and '__pycache__' not in p.parts)
    assert files, f'No exercise files: {folder}'
    target = directory / name
    with ZipFile(target, 'w', compression=ZIP_DEFLATED) as archive:
        for item in files:
            info = ZipInfo(item.relative_to(ROOT).as_posix(), date_time=(2026, 10, 31, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, item.read_bytes())
    return target.relative_to(ROOT).as_posix()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--staged-manifest', action='store_true', help='Hash Git index bytes after staging; required for publication on systems with line-ending conversion')
    options = parser.parse_args()
    kit = ROOT / 'examples/work-completion-kit'
    if kit.is_dir():
        for source, target, variable in [('project-example.json', 'project-example.js', 'WorkKitExample'),
                                         ('project-template.json', 'project-template.js', 'WorkKitTemplate')]:
            model = json.loads((kit / source).read_text(encoding='utf-8'))
            encoded = json.dumps(json.dumps(model, ensure_ascii=False), ensure_ascii=False)
            (kit / target).write_text('/* Generated from ' + source + '; edit the JSON source. */\n'
                                     + 'globalThis.' + variable + ' = JSON.parse(' + encoded + ');\n', encoding='utf-8')
    archives = [bundle('examples/claude-code-checks', 'reader-checks.zip'),
                bundle('examples/operations-edition', 'operations-practice.zip')]
    if kit.is_dir():
        archives.append(bundle('examples/work-completion-kit', 'work-completion-kit.zip'))
    files = READERS + ['start-here.html', 'sales.html', 'ai-bible.html', 'en/first-workflow.html',
                      'en/sales.html', 'en/ai-bible-global.html', 'en/media-kit.html',
                      'assets/learning-edition-20261031.css', 'assets/reader-sharing-20261031.js', 'en/edition-guide.css',
                      'examples/learning-edition/volume2-starter.zip']
    files += ['en/' + item for item in READERS]
    files += archives
    folders = ['examples/learning-edition', 'examples/claude-code-checks', 'examples/operations-edition']
    if kit.is_dir():
        folders.append('examples/work-completion-kit')
    for folder in folders:
        files.extend(item.relative_to(ROOT).as_posix() for item in (ROOT / folder).rglob('*')
                     if item.is_file() and item.suffix in {'.py', '.md', '.json', '.csv', '.html', '.js', '.cjs'} and '__pycache__' not in item.parts)
    def digest(name):
        if options.staged_manifest:
            content = subprocess.run(['git', 'show', ':' + name], cwd=ROOT, capture_output=True, check=True).stdout
        else:
            content = (ROOT / name).read_bytes()
        return sha256(content).hexdigest()
    manifest = {'edition': EDITION, 'date': '2026-10-31',
                'hash_source': 'git-index' if options.staged_manifest else 'working-tree',
                'scope': 'Korean volumes 1-5; English guides and selected reader corrections',
                'files': {name: digest(name) for name in sorted(set(files))}}
    (ROOT / 'release-20261031.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'edition': EDITION, 'files': len(manifest['files']), 'archives': archives}))

if __name__ == '__main__':
    main()
