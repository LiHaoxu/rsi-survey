#!/usr/bin/env python3
"""Check generated HTML anchors, local files, metadata, and source consistency."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,unquote
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag in ('a','link') and 'href' in a:self.links.append(a['href'])
        if tag=='script' and 'src' in a:self.links.append(a['src'])
p=Page();p.feed((ROOT/'index.html').read_text())
assert len(p.ids)==len(set(p.ids)), 'Duplicate HTML IDs'
for raw in p.links:
    u=urlparse(raw)
    if u.scheme or u.netloc:continue
    if not u.path:
        assert not u.fragment or unquote(u.fragment) in p.ids, f'Broken anchor: {raw}'
    elif not u.path.startswith('../'):
        assert (ROOT/unquote(u.path)).exists(),f'Missing file: {raw}'
records=json.loads((ROOT/'data/papers.json').read_text())
config=json.loads((ROOT/'config.json').read_text())
recent=json.loads((ROOT/'data/recent.json').read_text())
classics=json.loads((ROOT/'data/classics.json').read_text())
assert config['recent_end'] - config['recent_start'] == 4, 'Recent window must cover five publication years'
assert all(config['recent_start'] <= r['year'] <= config['recent_end'] for r in recent), 'Paper outside recent window'
assert all(r['year'] < config['recent_start'] for r in classics), 'Recent paper in background source'
assert {r['id'] for r in records} == {r['id'] for r in recent+classics}, 'Generated catalog differs from sources'
assert all(r['id'] in p.ids for r in records)
assert len(records)==len({r['id'] for r in records})
assert all(r['sources'] and r['influence_reason'] and r.get('bib_authors') for r in records)
review_path=ROOT/'data/selection-review.json'
if review_path.exists():
    review=json.loads(review_path.read_text())
    included={r['id'] for r in records}
    assert all(r['id'] in included for r in review['added']), 'Added paper missing from catalog'
    assert all(r['id'] not in included and r['id'] in p.ids for r in review['removed']), 'Removed-paper notice missing'
    assert all(r['id'] not in included for r in review['not_selected']), 'Deferred candidate appears in catalog'
print(f'PASS: {len(records)} papers, {len(p.ids)} unique anchors, {len(p.links)} links and assets checked')
