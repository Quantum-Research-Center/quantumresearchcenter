"""Watch OpenAI, Google and Anthropic for new announcements and research releases.

Usage:
    python3 scripts/ai_lab_watch.py            # list items not seen before (nothing is recorded)
    python3 scripts/ai_lab_watch.py --record   # list them, then record them as seen
    python3 scripts/ai_lab_watch.py --days 7   # also list already-seen dated items from the last 7 days

State lives in content/ai-lab-watch.json: for each source, the item URLs already seen. A source that cannot be
read is reported and keeps its previous state, so a failed fetch never hides an item. GitHub requests use
GITHUB_TOKEN when it is set (the anonymous limit is 60 requests an hour; one run uses about six).
"""
import argparse
import gzip
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'content/ai-lab-watch.json'
AGENT = 'Mozilla/5.0 (compatible; research-news-watch)'
# Titles matching this are marked, because they are the likeliest to be claims about known problems.
FLAG = re.compile(r'(?i)\b(quantum|qubits?|proofs?|prove[sd]?|proving|theorems?|conjectures?|lean|formal(ly|ization)?|mathemat\w*|open problems?|solv\w*|lower bounds?|algorithms?|physics|lattice|science)\b')

SOURCES = [
    # (id, lab, kind, location)
    ('openai-news', 'OpenAI', 'rss', 'https://openai.com/news/rss.xml'),
    ('openai-math-preprints', 'OpenAI', 'github-dir', 'openai/math/preprints'),
    ('openai-repos', 'OpenAI', 'github-org', 'openai'),
    ('deepmind-blog', 'Google', 'rss', 'https://deepmind.google/blog/rss.xml'),
    ('google-research-blog', 'Google', 'rss', 'https://research.google/blog/rss/'),
    ('deepmind-repos', 'Google', 'github-org', 'google-deepmind'),
    ('anthropic-news', 'Anthropic', 'links', 'https://www.anthropic.com/news'),
    ('anthropic-research', 'Anthropic', 'links', 'https://www.anthropic.com/research'),
    ('anthropic-formal-math', 'Anthropic', 'github-dir', 'anthropics/formal-math'),
    ('anthropic-repos', 'Anthropic', 'github-org', 'anthropics'),
]


def fetch(url, accept=None):
    headers = {'User-Agent': AGENT}
    if accept:
        headers['Accept'] = accept
    if url.startswith('https://api.github.com/') and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40) as response:
        data = response.read()
    # Some servers (deepmind.google) send gzip even when it was not requested.
    return gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data


def when(text):
    """Parse an RSS or Atom date into YYYY-MM-DD, or None."""
    if not text:
        return None
    try:
        return parsedate_to_datetime(text).astimezone(timezone.utc).date().isoformat()
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(text.strip().replace('Z', '+00:00')).date().isoformat()
    except ValueError:
        return None


def parse_feed(data):
    """Items of an RSS 2.0 or Atom feed as dicts with url, title, date."""
    root = ET.fromstring(data)
    items = []
    for item in root.iter('item'):
        url = (item.findtext('link') or item.findtext('guid') or '').strip()
        items.append({'url': url, 'title': (item.findtext('title') or '').strip(), 'date': when(item.findtext('pubDate'))})
    atom = '{http://www.w3.org/2005/Atom}'
    for entry in root.iter(atom + 'entry'):
        link = entry.find(atom + 'link')
        url = link.get('href', '') if link is not None else ''
        items.append({'url': url, 'title': (entry.findtext(atom + 'title') or '').strip(),
                      'date': when(entry.findtext(atom + 'published') or entry.findtext(atom + 'updated'))})
    return [i for i in items if i['url']]


def parse_links(data, base):
    """Article links on a listing page without a feed (Anthropic's /news and /research)."""
    section = '/' + base.rstrip('/').rsplit('/', 1)[-1] + '/'
    origin = re.match(r'https://[^/]+', base).group(0)
    slugs = sorted(set(re.findall(r'href="(' + re.escape(section) + r'[a-z0-9][a-z0-9-]*)"', data.decode('utf-8', 'replace'))))
    return [{'url': origin + s, 'title': s.rsplit('/', 1)[-1].replace('-', ' '), 'date': None} for s in slugs]


def read_source(kind, location):
    if kind == 'rss':
        return parse_feed(fetch(location))
    if kind == 'links':
        return parse_links(fetch(location), location)
    if kind == 'github-dir':
        repo, _, path = location.partition('/')[2].partition('/')
        owner = location.split('/')[0]
        entries = json.loads(fetch(f'https://api.github.com/repos/{owner}/{repo}/contents/{path}', 'application/vnd.github+json'))
        return [{'url': e['html_url'], 'title': e['name'], 'date': None} for e in entries
                if e['type'] == 'dir' and not e['name'].startswith('.')]
    if kind == 'github-org':
        repos = json.loads(fetch(f'https://api.github.com/orgs/{location}/repos?sort=created&direction=desc&per_page=30',
                                 'application/vnd.github+json'))
        return [{'url': r['html_url'], 'title': r['name'] + (' — ' + r['description'] if r.get('description') else ''),
                 'date': r['created_at'][:10]} for r in repos]
    raise ValueError('unknown source kind ' + kind)


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {'checked_on': None, 'seen': {}}


def new_items(items, seen):
    seen = set(seen)
    return [i for i in items if i['url'] not in seen]


def report(lab, source, items, label):
    for i in items:
        mark = '*' if FLAG.search(i['title']) else ' '
        print(f"  {mark} [{lab}] {i['date'] or '          '}  {i['title'][:110]}\n      {i['url']}   ({source}, {label})")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--record', action='store_true', help='record the listed items as seen')
    parser.add_argument('--days', type=int, default=0, help='also list seen items dated within this many days')
    args = parser.parse_args(argv)
    state = load_state()
    failures, total = [], 0
    since = (date.today() - timedelta(days=args.days)).isoformat() if args.days else None
    for ident, lab, kind, location in SOURCES:
        try:
            items = read_source(kind, location)
        except Exception as error:  # report and keep the old state for this source
            failures.append(f'{ident}: {error}')
            continue
        fresh = new_items(items, state['seen'].get(ident, []))
        if ident not in state['seen'] and not args.record:
            print(f'{ident}: not initialised; run with --record once to take a baseline ({len(items)} items)')
            fresh = []
        report(lab, ident, fresh, 'new')
        total += len(fresh)
        if since:
            report(lab, ident, [i for i in items if i not in fresh and i['date'] and i['date'] >= since], 'recent')
        if args.record:
            state['seen'][ident] = sorted(set(state['seen'].get(ident, [])) | {i['url'] for i in items})
    print(f'{total} new item(s); * marks titles about proofs, algorithms, quantum or mathematics.')
    for f in failures:
        print('could not read ' + f, file=sys.stderr)
    if args.record:
        state['checked_on'] = date.today().isoformat()
        STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False) + '\n')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
