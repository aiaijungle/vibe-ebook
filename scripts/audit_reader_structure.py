"""Read-only document structure and static fragment audit (generated targets may be absent)."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FILES = ['book1.html', 'index.html', 'agent-bible.html', 'claude-code-bible.html',
         'practical-bible.html', 'start-here.html', 'sales.html', 'ai-bible.html',
         'en/first-workflow.html', 'en/sales.html', 'en/ai-bible-global.html']

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.fragments = set()
        self.headings = Counter()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag in ('h1', 'h2', 'h3'):
            self.headings[tag] += 1
        href = attrs.get('href', '')
        if tag == 'a' and href.startswith('#') and len(href) > 1:
            self.fragments.add(href[1:])

def main():
    result = []
    for name in FILES:
        doc = Document()
        doc.feed((ROOT / name).read_text(encoding='utf-8'))
        counts = Counter(doc.ids)
        result.append({'file': name, 'headings': dict(doc.headings),
                       'duplicate_ids': [key for key, value in counts.items() if value > 1],
                       'unresolved_static_fragments': sorted(doc.fragments - counts.keys())})
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
