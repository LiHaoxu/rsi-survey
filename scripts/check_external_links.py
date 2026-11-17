#!/usr/bin/env python3
"""Advisory HTTP check: report uncertain links, never silently delete sources."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from urllib.parse import urldefrag, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        url = dict(attrs).get('href', '')
        if tag == 'a' and urlsplit(url).scheme in ('https', 'http'):
            # Issue forms are workflow entry points, not bibliographic sources.
            if '/issues/new' not in url:
                self.urls.add(urldefrag(url)[0])


def inspect(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'RSI-Atlas-Link-Check/1.1 (public research bibliography)'})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            return {'url': url, 'status': status, 'state': 'ok', 'resolved_url': response.url}
    except urllib.error.HTTPError as error:
        state = 'restricted' if error.code in (401, 403, 429) else 'needs_review'
        return {'url': url, 'status': error.code, 'state': state}
    except (OSError, ValueError) as error:
        return {'url': url, 'status': None, 'state': 'unverified', 'error': str(error)[:240]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='link-report.json')
    parser.add_argument('--limit', type=int, default=0, help='Optional smoke-check limit; 0 checks every link')
    args = parser.parse_args()
    links = Links()
    for path in ROOT.glob('*.html'):
        links.feed(path.read_text())
    urls = sorted(links.urls)
    if args.limit:
        urls = urls[:args.limit]
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(inspect, urls))
    counts = Counter(row['state'] for row in records)
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'total': len(records), 'counts': dict(counts), 'links': records}
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    lines = ['# External link review', '', f'Checked {len(records)} unique URLs. ' + ', '.join(f'{k}: {v}' for k, v in sorted(counts.items())), '', 'HTTP failures are review signals, not proof that a paper or repository is gone. Restricted sites and timeouts need manual verification. The complete JSON report is attached as a workflow artifact.', '']
    for row in records:
        if row['state'] != 'ok':
            lines.append(f'- {row["state"]} / {row["status"] or "network"}: {row["url"]}')
    summary = '\n'.join(lines) + '\n'
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as handle:
            handle.write(summary)
    print(summary)


if __name__ == '__main__':
    main()
