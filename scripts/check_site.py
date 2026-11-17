#!/usr/bin/env python3
"""Check generated local pages and relationship snapshots without network access."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids, self.links = [], []
        self.feed(path.read_text())
        assert len(self.ids) == len(set(self.ids)), f'Duplicate IDs: {path.name}'

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attr in ('href', 'src'):
            if attr in attrs:
                self.links.append(attrs[attr])


def check():
    connections = json.loads((ROOT / 'data/connections.json').read_text())
    config = json.loads((ROOT / 'config.json').read_text())
    is_survey = 'recent_start' in config
    peer = urlsplit(config['bench_url'] if is_survey else config['survey_url']).path.split('/')[1]
    peer_pages = {'index.html', 'changelog.html'} | ({'protocols.html', 'results.html'} if peer == 'rsi-bench' else set())
    pages = {path.resolve(): Page(path) for path in ROOT.glob('*.html')}
    assert (ROOT / 'changelog.html').resolve() in pages, 'Missing release history'
    checked = 0
    for path, page in list(pages.items()):
        for raw in page.links:
            url = urlsplit(raw)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            # Standalone CI may omit only the configured sibling, never arbitrary paths.
            if not target.is_relative_to(ROOT):
                assert target.parent == ROOT.parent / peer and target.name in peer_pages, f'Unknown cross-site target: {raw}'
                if not target.exists():
                    if url.fragment:
                        if target.name == 'protocols.html':
                            anchors = {row['id'] for row in connections['protocols']} | {'main'}
                        elif target.name == 'index.html':
                            rows = connections['resources' if peer == 'rsi-bench' else 'papers']
                            static = {'main', 'principles', 'catalog'} if peer == 'rsi-bench' else {'top', 'main', 'catalog', 'taxonomy', 'reading', 'questions', 'scope', 'catalog-data', 'aicl-2024', 'usb-rec-2025'}
                            anchors = {row['id'] for row in rows} | static
                        else:
                            anchors = {'main', 'submission'} if target.name == 'results.html' else {'top', 'main', 'v1.0', 'v1.1'}
                        assert unquote(url.fragment) in anchors, f'Unknown cross-site anchor: {raw}'
                    continue
            assert target.exists(), f'Missing file: {path.name} -> {raw}'
            if url.fragment and target.suffix == '.html':
                if target not in pages:
                    pages[target] = Page(target)
                assert unquote(url.fragment) in pages[target].ids, f'Broken anchor: {path.name} -> {raw}'
            checked += 1
    connections = json.loads((ROOT / 'data/connections.json').read_text())
    indexes = {}
    for name in ('papers', 'resources', 'protocols'):
        rows = connections[name]
        indexes[name] = {row['id'] for row in rows}
        assert len(rows) == len(indexes[name]), f'Duplicate {name} IDs'
    pairs = set()
    for row in connections['links']:
        key = (row['paper_id'], row['resource_id'], row['relation'])
        assert key not in pairs, f'Duplicate relation: {key}'
        pairs.add(key)
        assert row['paper_id'] in indexes['papers'] and row['resource_id'] in indexes['resources']
        assert row['relation'] in ('uses', 'implements', 'suggested') and row['note']
        if row['relation'] != 'suggested':
            assert row['sources'] and row['locator'], f'Missing factual evidence: {key}'
        assert all(urlsplit(url).scheme == 'https' and urlsplit(url).netloc for url in row['sources'])
    protocol_pairs = set()
    protocol_papers = set()
    for row in connections['protocol_links']:
        key = (row['paper_id'], row['protocol_id'])
        assert key not in protocol_pairs and row['note']
        protocol_pairs.add(key)
        assert row['paper_id'] not in protocol_papers, f'Multiple primary protocols: {row["paper_id"]}'
        protocol_papers.add(row['paper_id'])
        assert row['paper_id'] in indexes['papers'] and row['protocol_id'] in indexes['protocols']
    if (ROOT / 'data/papers.json').exists():
        actual = json.loads((ROOT / 'data/papers.json').read_text())
        assert {p['id'] for p in actual} == indexes['papers'], 'Stale paper snapshot'
        lookup = {p['id']: p for p in actual}
        assert all(all(p[k] == lookup[p['id']][k] for k in ('short', 'title', 'year', 'venue')) for p in connections['papers'])
    if (ROOT / 'data/resources.json').exists():
        actual = json.loads((ROOT / 'data/resources.json').read_text())
        assert {p['id'] for p in actual['datasets'] + actual['tools']} == indexes['resources'], 'Stale resource snapshot'
        assert {p['id'] for p in actual['protocols']} == indexes['protocols'], 'Stale protocol snapshot'
        resource_map = {p['id']: (p['name'], kind) for kind, group in [('dataset', 'datasets'), ('tool', 'tools')] for p in actual[group]}
        assert all((p['name'], p['type']) == resource_map[p['id']] for p in connections['resources']), 'Stale resource metadata'
        protocol_map = {p['id']: p['title'] for p in actual['protocols']}
        assert all(p['title'] == protocol_map[p['id']] for p in connections['protocols']), 'Stale protocol metadata'
    print(f'PASS: {len(list(ROOT.glob("*.html")))} pages, {checked} local links, {len(pairs)} resource connections, {len(protocol_pairs)} protocol suggestions')


if __name__ == '__main__':
    check()
