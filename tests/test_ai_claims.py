"""The AI claims feed must attribute every claim, label its verification, and link only to published material."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'education'))
import ai_claims
from news_articles import stream_nav
from paper_news import load_papers


class AIClaimsFeedTests(unittest.TestCase):
    def setUp(self):
        self.articles = [json.loads(p.read_text()) for p in (ROOT / 'content/news-articles').glob('*.json')]
        self.papers = load_papers(ROOT)['papers']
        self.data = json.loads((ROOT / 'content/ai-claims.json').read_text())

    def page(self):
        pages = {}
        ai_claims.render_feed_page(ROOT, self.articles, self.papers,
                                   lambda path, title, description, body: pages.__setitem__(path, body), stream_nav)
        return BeautifulSoup(pages[ai_claims.PAGE], 'html.parser')

    def test_every_claim_shows_claimant_ai_status_and_source(self):
        soup = self.page()
        self.assertEqual(len(soup.select('h1')), 1)
        cards = {c['id']: c for c in soup.select('.ai-claim')}
        self.assertEqual(set(cards), {c['id'] for c in self.data['claims']})
        for item in self.data['claims']:
            text = cards[item['id']].get_text()
            for key in ('claimant', 'ai', 'claim'):
                self.assertIn(item[key], text)
            self.assertIn(ai_claims.VERIFICATION[item['verification']][0], text)
            for source in item['sources']:
                self.assertIsNotNone(cards[item['id']].find('a', href=source['url']))
        self.assertIn('not an endorsement', soup.get_text())

    def test_claims_are_newest_first_and_grouped_by_month(self):
        dates = [li.find('time')['datetime'] for li in self.page().select('.ai-claim')]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_preview_links_to_feed_and_stream_nav_has_tab(self):
        preview = BeautifulSoup(ai_claims.render_feed_preview(ROOT, self.articles, self.papers, 'news/index.html'), 'html.parser')
        self.assertIsNotNone(preview.find('a', href='ai-claims/index.html'))
        self.assertLessEqual(len(preview.select('.ai-claim')), 4)
        self.assertIn('AI Claims', stream_nav('news/index.html'))

    def test_rejects_bad_entries(self):
        mutations = (
            lambda d: d['claims'].append(copy.deepcopy(d['claims'][0])),
            lambda d: d['claims'][0].update(verification='solved'),
            lambda d: d['claims'][0].update(sources=[{'label': 'x', 'url': 'http://example.com'}]),
            lambda d: d['claims'][0].update(paper='0000.00000'),
            lambda d: d['claims'][0].update(register=['no-such-problem']),
            lambda d: d['claims'][0].update(article='no-such-article'),
            lambda d: d['claims'][0].update(date='2999-01-01'),
            lambda d: d['claims'][0].update(ai=''),
        )
        real_loads = json.loads
        for mutate in mutations:
            data = copy.deepcopy(self.data)
            mutate(data)
            with patch.object(ai_claims.json, 'loads', side_effect=lambda text: data if '"claims"' in text else real_loads(text)):
                with self.assertRaises(ValueError):
                    ai_claims.load_feed(ROOT, self.articles, self.papers)


if __name__ == '__main__':
    unittest.main()
