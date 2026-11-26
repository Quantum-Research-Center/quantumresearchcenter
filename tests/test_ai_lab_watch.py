"""The lab watcher must parse each kind of source and report only items it has not seen."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ai_lab_watch as watch

RSS = b'''<?xml version="1.0"?><rss version="2.0"><channel><title>Lab</title>
<item><title>Finding faster quantum algorithms</title><link>https://lab.example/a</link><pubDate>Mon, 23 Nov 2026 16:59:40 +0000</pubDate></item>
<item><title>Product news</title><guid>https://lab.example/b</guid></item></channel></rss>'''
ATOM = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>A proof</title><link href="https://lab.example/c"/>
<published>2026-11-20T10:00:00Z</published></entry></feed>'''
PAGE = b'<a href="/news/claude-proves-x">x</a><a href="/news/claude-proves-x">again</a><a href="/research/other">y</a>'


class LabWatchTests(unittest.TestCase):
    def test_parses_rss_and_atom(self):
        self.assertEqual(watch.parse_feed(RSS), [
            {'url': 'https://lab.example/a', 'title': 'Finding faster quantum algorithms', 'date': '2026-11-23'},
            {'url': 'https://lab.example/b', 'title': 'Product news', 'date': None}])
        self.assertEqual(watch.parse_feed(ATOM), [{'url': 'https://lab.example/c', 'title': 'A proof', 'date': '2026-11-20'}])

    def test_listing_page_links_are_deduplicated_and_scoped(self):
        self.assertEqual(watch.parse_links(PAGE, 'https://lab.example/news'),
                         [{'url': 'https://lab.example/news/claude-proves-x', 'title': 'claude proves x', 'date': None}])

    def test_only_unseen_items_are_new(self):
        items = watch.parse_feed(RSS)
        self.assertEqual([i['url'] for i in watch.new_items(items, ['https://lab.example/a'])], ['https://lab.example/b'])

    def test_flag_marks_research_titles_only(self):
        self.assertTrue(watch.FLAG.search('Finding faster quantum algorithms'))
        self.assertTrue(watch.FLAG.search('A step toward defining the Standard Model on a lattice'))
        self.assertFalse(watch.FLAG.search('How Amplitude ships product improvements'))

    def test_gzip_responses_are_decompressed(self):
        import gzip
        from unittest.mock import patch, MagicMock
        response = MagicMock()
        response.__enter__.return_value.read.return_value = gzip.compress(RSS)
        with patch.object(watch.urllib.request, 'urlopen', return_value=response):
            self.assertEqual(watch.fetch('https://lab.example/rss'), RSS)

    def test_state_file_covers_every_source(self):
        state = watch.load_state()
        self.assertEqual(set(state['seen']), {s[0] for s in watch.SOURCES})


if __name__ == '__main__':
    unittest.main()
