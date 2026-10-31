"""Validate learning modules, static dependencies and the release served over HTTP.

Run without arguments before publishing. With --base-url, also compare the deployed
release manifest and each listed file against the verified local edition.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
READERS = ['book1.html', 'index.html', 'agent-bible.html', 'claude-code-bible.html', 'practical-bible.html']
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.modules, self.refs, self.ids = [], [], [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get('class', '').split())
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if 'aib-edition-update' in classes:
            paid = any('aib-update-content' in item[1] and 'paywall-locked' in item[1] for item in self.stack)
            self.modules.append({'id': attrs.get('id'), 'inside_existing_paid_section': paid})
        for attr in ('src', 'href'):
            if attrs.get(attr):
                self.refs.append(attrs[attr])
        if tag not in VOID:
            self.stack.append((tag, classes))
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

def validate_local():
    output = []
    for name in READERS:
        parser = Reader()
        parser.feed((ROOT / name).read_text(encoding='utf-8'))
        assert len(parser.ids) == len(set(parser.ids)), f'Duplicate IDs: {name}'
        assert len(parser.modules) >= 2, f'Missing two substantive update modules: {name}'
        assert all(item['id'] and item['inside_existing_paid_section'] for item in parser.modules), f'Invalid module boundary: {name}'
        for reference in parser.refs:
            parts = urlsplit(reference)
            if parts.scheme or parts.netloc or not parts.path or parts.path.startswith('/'):
                continue
            target = (ROOT / unquote(parts.path)).resolve()
            if parts.path.startswith(('assets/', 'examples/')):
                assert target.is_relative_to(ROOT.resolve()) and target.is_file(), f'Missing local resource: {name}: {parts.path}'
        output.append({'file': name, 'modules': parser.modules})
    return output

def fetch_bytes(base, name, edition):
    url = base.rstrip('/') + '/' + name + '?edition=' + edition
    with urlopen(Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'AI-Bible-Release-Check'}), timeout=25) as response:
        assert response.status == 200, f'HTTP {response.status}: {name}'
        return response.read()

def validate_live(base):
    manifest = json.loads((ROOT / 'release-20261031.json').read_text(encoding='utf-8'))
    deployed = json.loads(fetch_bytes(base, 'release-20261031.json', manifest['edition']))
    assert deployed == manifest, 'Deployment has not yet published this release manifest'
    def check(item):
        name, expected = item
        data = fetch_bytes(base, name, manifest['edition'])
        assert sha256(data).hexdigest() == expected, f'Deployed file differs: {name}'
        return name
    with ThreadPoolExecutor(max_workers=4) as executor:
        verified = list(executor.map(check, manifest['files'].items()))
    return {'edition': manifest['edition'], 'verified_live_files': verified}

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--base-url')
    options = args.parse_args()
    result = {'local': validate_local()}
    if options.base_url:
        result['live'] = validate_live(options.base_url)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
