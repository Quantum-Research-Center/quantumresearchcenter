"""A dated feed of AI-attributed claims about known problems, verified or not."""
import html
import json
import os
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

PAGE = 'news/ai-claims/index.html'
SLUG = r'[a-z0-9]+(?:-[a-z0-9]+)*'
# Ordered from least to most established, then refuted. Each label says what has and has not been checked.
VERIFICATION = {
    'unverified': ('Unverified', 'Announced or posted as a preprint; no independent check has been reported.'),
    'under-review': ('Under external review', 'A named group is examining the work; no verdict has been published.'),
    'partly-formal': ('Partly machine-checked', 'Some statements are checked by a proof assistant; the rest is not.'),
    'formal': ('Machine-checked', 'A proof assistant has checked the stated result; human understanding and review may still be pending.'),
    'disputed': ('Disputed', 'Published objections to correctness remain unresolved.'),
    'confirmed': ('Independently confirmed', 'Peer review or independent experts have confirmed the result.'),
    'refuted': ('Refuted or withdrawn', 'An error was found, or the claimants withdrew the claim.'),
}
REQUIRED = ('field', 'problem', 'known_since', 'claimant', 'ai', 'claim', 'summary')


def esc(value):
    return html.escape(str(value), quote=True)


def relative(target, source):
    return os.path.relpath(target, Path(source).parent).replace(os.sep, '/')


def long_date(value):
    day = date.fromisoformat(value)
    return f'{day.day} {day.strftime("%B %Y")}'


def load_feed(root, articles, papers):
    """Validate the feed against approved papers, the problem register, and published articles."""
    path = root / 'content/ai-claims.json'
    if not path.exists():
        return {'reviewed_on': None, 'claims': []}
    data = json.loads(path.read_text())
    reviewed = date.fromisoformat(data['reviewed_on'])
    approved = {p['id'] for p in papers if p['status'] == 'approved'}
    public = {a['slug'] for a in articles if a['status'] == 'published'}
    register = json.loads((root / 'content/ai-problem-claims.json').read_text())['problems']
    register_ids = {p['id'] for p in register}
    seen = set()
    for item in data['claims']:
        ident = item.get('id', '')
        if not re.fullmatch(SLUG, ident) or ident in seen:
            raise ValueError('Invalid or duplicate AI claim ID: ' + ident)
        seen.add(ident)
        for key in REQUIRED:
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'AI claim {ident} is missing {key}')
        if item.get('verification') not in VERIFICATION:
            raise ValueError(f'AI claim {ident} has an unknown verification status')
        if date.fromisoformat(item['date']) > reviewed:
            raise ValueError(f'AI claim {ident} is dated after the review date')
        if not item.get('sources'):
            raise ValueError(f'AI claim {ident} needs at least one source')
        for source in item['sources']:
            url = urlsplit(source.get('url', ''))
            if url.scheme != 'https' or not url.netloc or not source.get('label', '').strip():
                raise ValueError(f'AI claim {ident} needs labelled HTTPS sources')
        if item.get('paper') and item['paper'] not in approved:
            raise ValueError(f'AI claim {ident} links a paper that is not approved')
        for reg in item.get('register', []):
            if reg not in register_ids:
                raise ValueError(f'AI claim {ident} links an unknown register entry')
        if item.get('article') and item['article'] not in public:
            raise ValueError(f'AI claim {ident} links an article that is not published')
    data['claims'] = sorted(data['claims'], key=lambda c: c['date'], reverse=True)
    return data


def entry(item, source, heading='h3'):
    label, meaning = VERIFICATION[item['verification']]
    links = ''.join(f'<a href="{esc(s["url"])}">{esc(s["label"])} ↗</a>' for s in item['sources'])
    if item.get('paper'):
        links += f'<a href="{relative("news/papers/" + item["paper"] + "/index.html", source)}">Our paper summary</a>'
    if item.get('article'):
        links += f'<a href="{relative("news/articles/" + item["article"] + "/index.html", source)}">Background article</a>'
    for reg in item.get('register', []):
        links += f'<a href="{relative("ai-problem-claims/index.html", source)}#{esc(reg)}">Problem register</a>'
        break
    return f'''<li class="ai-claim" id="{esc(item['id'])}">
<p class="ai-claim-meta"><time datetime="{item['date']}">{long_date(item['date'])}</time><span>{esc(item['field'])}</span></p>
<{heading}><a href="{relative(PAGE, source)}#{esc(item['id'])}">{esc(item['problem'])}</a></{heading}>
<p class="ai-claim-known">{esc(item['known_since'])}</p>
<p class="ai-claim-status"><span class="ai-claim-badge ai-claim-{item['verification']}" title="{esc(meaning)}">{esc(label)}</span><span class="ai-claim-type">{esc(item['claim'])}</span></p>
<dl class="ai-claim-who"><div><dt>Claimant</dt><dd>{esc(item['claimant'])}</dd></div><div><dt>AI</dt><dd>{esc(item['ai'])}</dd></div></dl>
<p class="ai-claim-summary">{esc(item['summary'])}</p>
<div class="problem-links">{links}</div>
</li>'''


def legend():
    return '<dl class="ai-claim-legend">' + ''.join(
        f'<div><dt><span class="ai-claim-badge ai-claim-{key}">{esc(label)}</span></dt><dd>{esc(meaning)}</dd></div>'
        for key, (label, meaning) in VERIFICATION.items()) + '</dl>'


INTRO = ('Claims that an AI system found or substantially produced a solution to a known problem, collected as they '
         'are announced, whether or not anyone has checked them yet. Each entry names who made the claim and which AI '
         'it credits, and gives a verification status. An entry records a claim; it is not an endorsement.')


def render_feed_page(root, articles, papers, shell, stream_nav):
    data = load_feed(root, articles, papers)
    if not data['claims']:
        return
    source = PAGE
    months = {}
    for item in data['claims']:
        months.setdefault(item['date'][:7], []).append(item)
    body = ('<header class="editorial-intro compact"><p class="eyebrow">News</p><h1>AI Claims</h1>'
            f'<p>{esc(INTRO)}</p></header>' + stream_nav(source, 'ai-claims'))
    body += ('<details class="ai-claim-key"><summary>What the verification labels mean</summary>' + legend()
             + f'<p class="problem-review">For the major named problems, the <a href="{relative("ai-problem-claims/index.html", source)}">problem register</a> tracks each claim with its scope. Entries are reviewed as new reviews, formalizations and corrections appear; sources reviewed <time datetime="{data["reviewed_on"]}">{long_date(data["reviewed_on"])}</time>.</p></details>')
    for month, items in months.items():
        title = date.fromisoformat(month + '-01').strftime('%B %Y')
        body += (f'<section class="ai-claims-month" aria-labelledby="month-{month}"><h2 id="month-{month}">{title}</h2>'
                 '<ol class="ai-claims-list">' + ''.join(entry(i, source) for i in items) + '</ol></section>')
    shell(source, 'AI Claims', 'Dated claims that AI systems solved or substantially solved known problems, with claimants, sources and verification status.', body)


def render_feed_preview(root, articles, papers, source, count=4):
    data = load_feed(root, articles, papers)
    if not data['claims']:
        return ''
    items = ''.join(entry(i, source) for i in data['claims'][:count])
    return (f'<section class="ai-claims-preview" aria-labelledby="ai-claims-title"><div class="section-top"><div><p class="eyebrow">Claims</p>'
            f'<h2 id="ai-claims-title">AI claims on known problems</h2></div><a href="{relative(PAGE, source)}">All AI claims ↗</a></div>'
            '<p class="section-intro">The newest claims that an AI system solved a known problem, with who claims it and how far it has been checked.</p>'
            f'<ol class="ai-claims-list">{items}</ol></section>')
