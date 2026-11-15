import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from games import validate  # noqa: E402


class GamesTests(unittest.TestCase):
    def test_catalogue_lists_every_game_page(self):
        data = json.loads((ROOT / 'content/games.json').read_text())
        validate(ROOT, data)
        index = (ROOT / 'games/index.html').read_text()
        for game in data['games']:
            with self.subTest(game=game['id']):
                self.assertIn(f'href="{Path(game["href"]).name}"', index)
                self.assertTrue((ROOT / game['href']).is_file())

    def test_validation_rejects_pages_outside_the_section(self):
        bad = {'games': [{'id': 'x', 'kind': 'Puzzle', 'title': 'X', 'summary': 'S', 'href': 'tools/x.html'}]}
        with self.assertRaises(ValueError):
            validate(ROOT, bad)

    def test_bunch_page_has_every_element_its_script_uses(self):
        page = (ROOT / 'games/quantum-2028.html').read_text()
        script = (ROOT / 'games/quantum-2028.js').read_text()
        ids = set(re.findall(r"getElementById\('([^']+)'\)", script))
        self.assertTrue(ids)
        for ident in ids:
            self.assertIn(f'id="{ident}"', page)
        self.assertRegex(page, r'<script defer src="quantum-2028\.js(\?v=[0-9a-f]+)?"></script>')
        self.assertIn('role="status"', page)

    def test_bunch_explains_the_physics_with_typeset_math(self):
        page = (ROOT / 'games/quantum-2028.html').read_text()
        self.assertIn(r'\ket{1,1}', page)
        self.assertIn('tex-svg.js', page)
        self.assertIn('What the game changes', page)

    @unittest.skipUnless(shutil.which('node'), 'Node.js is not installed')
    def test_quantum_2028_rules(self):
        result = subprocess.run(['node', str(ROOT / 'tests/js/quantum_2028_rules.js')], capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_storage_access_is_guarded(self):
        script = (ROOT / 'games/quantum-2028.js').read_text()
        self.assertEqual(script.count('localStorage'), len(re.findall(r'try \{ (?:return )?window\.localStorage', script)))


if __name__ == '__main__':
    unittest.main()
