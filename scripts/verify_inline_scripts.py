"""Check inline JavaScript syntax without executing page code or external requests."""
from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FILES = ['book1.html', 'index.html', 'agent-bible.html',
         'claude-code-bible.html', 'practical-bible.html']
if (ROOT / 'examples/work-completion-kit/workbench.html').is_file():
    FILES.append('examples/work-completion-kit/workbench.html')

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.current = None
        self.scripts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attrs = dict(attrs)
            kind = attrs.get('type', '').lower()
            self.current = [] if not attrs.get('src') and kind in ('', 'text/javascript', 'application/javascript', 'module') else None
    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)
    def handle_endtag(self, tag):
        if tag == 'script' and self.current is not None:
            self.scripts.append(''.join(self.current))
            self.current = None

def main():
    checked, failures = 0, []
    with tempfile.TemporaryDirectory(prefix='bible-syntax-') as temp:
        target = Path(temp) / 'inline.mjs'
        for name in FILES:
            parser = Scripts()
            parser.feed((ROOT / name).read_text(encoding='utf-8'))
            for index, script in enumerate(parser.scripts, 1):
                if not script.strip():
                    continue
                target.write_text(script, encoding='utf-8')
                result = subprocess.run(['node', '--check', str(target)], capture_output=True, text=True)
                checked += 1
                if result.returncode:
                    failures.append({'file': name, 'inline_script': index})
    print(json.dumps({'checked': checked, 'failures': failures}))
    raise SystemExit(bool(failures))

if __name__ == '__main__':
    main()
