#!/usr/bin/env python3
"""Check generated HTML anchors, local files, metadata, and source consistency."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,unquote
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.entries=[];self.views=[];self.sort_options=[];self.entry_links={};self.current_entry=None;self.in_sort=False;self.details_count=0;self.catalog_view=None;self.quick_years=[];self.quick_code=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag in ('a','link') and 'href' in a:self.links.append(a['href'])
        if tag=='script' and 'src' in a:self.links.append(a['src'])
        if tag=='article' and 'data-entry' in a:
            self.entries.append(a);self.current_entry=a['id'];self.entry_links[self.current_entry]=[]
        if tag=='a' and self.current_entry:self.entry_links[self.current_entry].append(a.get('href',''))
        if tag=='button' and 'data-view' in a:self.views.append((a['data-view'],a.get('aria-pressed')))
        if tag=='button' and 'data-quick-year' in a:self.quick_years.append(a['data-quick-year'])
        if tag=='button' and 'data-quick-code' in a:self.quick_code=True
        if tag=='select' and 'data-sort' in a:self.in_sort=True
        if tag=='option' and self.in_sort:self.sort_options.append(a['value'])
        if tag=='details' and self.current_entry:self.details_count+=1
        if 'data-entries' in a:self.catalog_view=a.get('data-view')
    def handle_endtag(self,tag):
        if tag=='article':self.current_entry=None
        if tag=='select':self.in_sort=False
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
assert {r['id']:r for r in records} == {r['id']:r for r in recent+classics}, 'Generated catalog differs from sources'
assert all(r['id'] in p.ids for r in records)
assert len(records)==len({r['id'] for r in records})
assert all(r['sources'] and r['influence_reason'] and r.get('bib_authors') for r in records)
assert len(p.entries)==len(records), 'Catalog must use exactly one DOM entry per paper'
assert {r['id'] for r in records}=={a['id'] for a in p.entries}, 'Rendered papers differ from data'
assert p.catalog_view=='list', 'Default view must be compact list'
assert p.views==[('list','true'),('cards','false')], 'Accessible list/card controls missing'
assert p.sort_options==['newest','oldest','title'], 'Expected chronological and title sorting'
assert set(p.quick_years)=={'recent','background'} and p.quick_code, 'Quick filters missing'
assert p.details_count==len(records), 'Every paper needs one expandable details section'
assert all(a.get('data-title') and a.get('data-period') in ('recent','background') for a in p.entries), 'Sorting/filter metadata missing'
assert 'changelog.html' in p.links, 'Update history link missing'
assert any('template=paper.yml' in u for u in p.links) and any('template=correction.yml' in u for u in p.links), 'Maintenance links missing'
connections_path=ROOT/'data/connections.json'
if connections_path.exists():
    connections=json.loads(connections_path.read_text())
    resources={r['id'] for r in connections['resources']}
    protocols={r['id'] for r in connections['protocols']}
    for item in connections['links']:
        assert item['paper_id'] in p.entry_links and item['resource_id'] in resources, 'Unknown relationship endpoint'
        assert item['relation'] in ('uses','implements','suggested'), 'Unknown resource relationship'
        assert config['bench_url']+'#'+item['resource_id'] in p.entry_links[item['paper_id']], 'Resource link missing from paper'
        assert all(u in p.entry_links[item['paper_id']] for u in item.get('sources',[])), 'Relationship evidence missing'
    for item in connections['protocol_links']:
        assert item['paper_id'] in p.entry_links and item['protocol_id'] in protocols, 'Unknown protocol endpoint'
        url=config['bench_url'].rsplit('/',1)[0]+'/protocols.html#'+item['protocol_id']
        assert url in p.entry_links[item['paper_id']], 'Suggested protocol missing from paper'
    html=(ROOT/'index.html').read_text()
    if connections['protocol_links'] or any(r['relation']=='suggested' for r in connections['links']):
        assert '不表示原论文已经使用这些资源' in html and 'editorial-connections' in html, 'Editorial suggestions must be labeled separately'
review_path=ROOT/'data/selection-review.json'
if review_path.exists():
    review=json.loads(review_path.read_text())
    included={r['id'] for r in records}
    assert all(r['id'] in included for r in review['added']), 'Added paper missing from catalog'
    assert all(r['id'] not in included and r['id'] in p.ids for r in review['removed']), 'Removed-paper notice missing'
    assert all(r['id'] not in included for r in review['not_selected']), 'Deferred candidate appears in catalog'
print(f'PASS: {len(records)} papers, {len(p.ids)} unique anchors, {len(p.links)} links and assets checked')
