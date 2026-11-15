"""The Games section: a catalogue of puzzles built on quantum rules, and one page per game.

Each game's logic is a hand-written script in games/; this module writes the HTML around it."""
import json
import os
import re
from html import escape
from pathlib import Path

ASSETS = '<link rel="stylesheet" href="games.css">'


def relative(target, source):
    return os.path.relpath(target, Path(source).parent).replace(os.sep, '/')


def validate(root, data):
    ids = set()
    for game in data['games']:
        if game['id'] in ids:
            raise ValueError('Duplicate game ID: ' + game['id'])
        ids.add(game['id'])
        if not re.fullmatch(r'games/[a-z0-9]+(?:-[a-z0-9]+)*\.html', game['href']):
            raise ValueError('Game links must be pages inside games/: ' + game['href'])
        if not all(game[field].strip() for field in ('kind', 'title', 'summary')):
            raise ValueError('Every game needs a kind, title and summary')
        script = root / game['href'].replace('.html', '.js')
        if not script.is_file():
            raise ValueError('Missing game script: ' + script.relative_to(root).as_posix())


def game_card(index, game, source):
    e = escape
    ideas = ''.join(f'<li>{e(idea)}</li>' for idea in game.get('ideas', []))
    return (f'<li class="game-card"><p class="game-index" aria-hidden="true">{index:02}</p>'
            f'<div><p class="game-kind">{e(game["kind"])}</p>'
            f'<h3><a href="{e(relative(game["href"], source))}">{e(game["title"])}</a></h3>'
            f'<p class="game-summary">{e(game["summary"])}</p>'
            + (f'<ul class="game-ideas" aria-label="Quantum ideas in play">{ideas}</ul>' if ideas else '')
            + '</div></li>')


def render_quantum_2028(shell):
    cells = '<span></span>' * 16
    lab = ('<section class="game-lab" aria-labelledby="bunch-lab-heading">'
           '<h2 class="sr-only" id="bunch-lab-heading">Play Quantum 2028</h2>'
           '<figure class="bunch-figure">'
           '<div class="bunch-board" id="bunch-board" tabindex="0" role="application" hidden'
           ' aria-label="Quantum 2028 board. Use the arrow keys or W, A, S, D to slide the tiles.">'
           f'<div class="bunch-cells" aria-hidden="true">{cells}</div>'
           '<svg class="bunch-links" id="bunch-links" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"></svg>'
           '<div class="bunch-pieces" id="bunch-pieces"></div></div>'
           '<figcaption>Click the board, then slide with the arrow keys or W, A, S, D; on a touch screen, swipe.'
           ' A dashed tile is one tile split over two cells, joined by a dashed line: tap either half to observe it.'
           ' Keyboard users can Tab to a split tile and press Enter.</figcaption>'
           '<noscript><p class="game-noscript">Quantum 2028 runs in your browser; enable JavaScript to play.</p></noscript>'
           '</figure>'
           '<div class="bunch-panel" id="bunch-panel" hidden>'
           '<dl class="bunch-scores"><div><dt>Score</dt><dd id="bunch-score">0</dd></div>'
           '<div><dt>Best</dt><dd id="bunch-best">0</dd></div>'
           '<div><dt>Flips</dt><dd id="bunch-flips">0</dd></div></dl>'
           '<div class="bunch-buttons"><button type="button" id="bunch-flip" aria-pressed="false"'
           ' title="Then choose a tile to change its sign">Flip a sign</button>'
           '<button type="button" id="bunch-new">New game</button></div>'
           '<p class="bunch-status" id="bunch-status" role="status" aria-live="polite"></p>'
           '<ul class="bunch-key" aria-label="Tile key">'
           '<li><span class="bunch-swatch" aria-hidden="true"></span>Plus tile, in one cell</li>'
           '<li><span class="bunch-swatch is-minus" aria-hidden="true"></span>Minus tile: cancels an equal plus tile</li>'
           '<li><span class="bunch-swatch is-split" aria-hidden="true"></span>Split tile: in two cells, each with probability ½</li></ul>'
           '<ol class="bunch-log" id="bunch-log" aria-label="Recent events"></ol>'
           '</div></section>')
    rules = ('<section class="game-reading" id="rules"><h2>How to play</h2><ol class="game-rules">'
             '<li>Each slide moves every tile as far as it can go. After each slide a 2 or a 4 appears in an'
             ' empty cell, and one in five arrives with a minus sign.</li>'
             '<li>Two equal tiles with the same sign <em>bunch</em>: they become one tile of twice the value,'
             ' held in both of the cells they slid into. The two dashed halves are one tile, not two.</li>'
             '<li>Tap a split tile to observe it. It is found in one of its two cells, each with probability'
             r' \(1/2\), and the other cell empties. Observing is free: no new tile appears.</li>'
             '<li>Slide the two halves of one tile into each other and they rejoin, in the cell you chose, with'
             ' no chance involved.</li>'
             '<li>When a half meets an equal tile, the contact observes it first. If the tile turns out to be in'
             ' that cell, the merge goes ahead; if not, that half vanishes and the other becomes certain.</li>'
             '<li>Two equal tiles of opposite sign cancel: both disappear and you score nothing, but two cells'
             ' open up.</li>'
             '<li>Flip a sign changes the sign of one tile. You start with two flips and earn one more every'
             ' eight merges.</li></ol>'
             '<p>Your score is the total value of the tiles you create. The game ends when no slide changes'
             ' the board and no split tile is left to observe.</p></section>')
    physics = ('<section class="game-reading" id="physics"><h2>The physics behind the rules</h2>'
               '<p>Send two identical photons into a half-silvered mirror, one from each side. Each photon is either'
               ' transmitted or reflected, so there are four ways for the pair to leave. Two of them put one photon'
               ' in each output, and their amplitudes are equal in size and opposite in sign, so they cancel. What'
               ' remains is the two photons leaving together:</p>'
               r'<p>\[\ket{1,1}\;\longrightarrow\;\tfrac{1}{\sqrt2}\bigl(\ket{2,0}-\ket{0,2}\bigr),\]</p>'
               r'<p>where \(\ket{m,n}\) means \(m\) photons in one output and \(n\) in the other. The pair leaves as'
               ' a single bunch, in an equal superposition of the two outputs. This is the Hong–Ou–Mandel effect,'
               ' measured in 1987, and it is the merge in Quantum 2028: two equal tiles become one bunch spread over'
               ' both cells. Photons that differ in colour, arrival time or polarisation do not interfere and leave'
               ' independently, which is why only equal tiles merge.</p>'
               r'<p>Each half of the bunch carries amplitude \(1/\sqrt2\), and the Born rule turns an amplitude'
               r' \(a\) into a probability \(|a|^2\), so each half is found with probability \(1/2\). Finding the'
               ' tile in one cell empties the other: that is collapse. Contact counts as observation because'
               ' whether a merge happens depends on where the tile is, so the board has to settle the question'
               ' before it can go on.</p>'
               '<p>Rejoining is interference used on purpose. A single particle sent along two paths and brought'
               ' back together at a second half-silvered mirror can leave by one port with certainty, if the two'
               ' paths are set up to reinforce there; this is the Mach–Zehnder interferometer. The game treats each'
               ' split tile as one particle in two places and always sets the paths to reinforce, so sliding the'
               ' halves together places the tile without chance.</p>'
               '<p>The signs are the same idea. Amplitudes carry signs, and amplitudes that lead to the same'
               ' outcome add, so equal and opposite ones cancel, exactly as the one-photon-each outcomes did above.'
               ' The flip is a phase shift, such as a Z gate on a qubit or a half-wave plate on a photon.</p>'
               '<p class="game-note">What the game changes. Values double because games need goals; photons carry'
               ' no score. Interference cancels amplitudes, not objects: real particles are never destroyed by'
               ' it, and the probability they lose in one place appears in another. A lone tile’s sign is'
               ' a global phase, which no experiment could detect; signs matter only between two things that'
               ' interfere. Sending the bunch back through a beam splitter would return the two separate photons'
               ' rather than one doubled tile. The faithful parts are the bunching of identical tiles, the equal'
               ' superposition, the probabilities of one half and the collapse.</p></section>')
    tries = ('<section class="game-reading" id="try"><h2>Things to try</h2><ol class="game-try">'
             '<li>Merge two 2s, then slide again along the same line: the halves of the 4 meet and rejoin.'
             ' Slide across the line instead and they drift apart, still one tile.</li>'
             '<li>Observe split tiles over a few games and count where they land: about half the time in each'
             ' cell, with no pattern you can exploit.</li>'
             '<li>When the board fills up, use a minus 2 to clear a 2: two cells open at once. Keep minus tiles'
             ' away from your largest plus tile, which they would cancel rather than grow.</li>'
             '<li>Before a risky contact, compare the two choices: observe now and live with the result, or spend'
             ' a slide rejoining the halves where you want the tile.</li></ol></section>')
    body = ('<header class="editorial-intro compact"><p class="eyebrow">Games / Quantum 2028</p>'
            '<h1>Quantum 2028: a merge that lands in two places</h1>'
            '<p>A sliding-tile puzzle built on how identical photons behave at a beam splitter. Equal tiles merge,'
            ' but the merged tile is held in both of their cells until you look, or until it meets another'
            ' tile.</p></header>' + lab + rules + physics + tries)
    shell('games/quantum-2028.html', 'Quantum 2028: a quantum merging puzzle',
          'A sliding-tile puzzle on quantum rules: equal tiles bunch into a superposition over two cells, observation collapses it, and opposite signs cancel.',
          body, assets=ASSETS + '<script defer src="quantum-2028.js"></script>')


def render_games(root, shell):
    data = json.loads((root / 'content/games.json').read_text())
    validate(root, data)
    count = len(data['games'])
    body = ('<header class="editorial-intro"><p class="eyebrow">Games / Quantum puzzles</p>'
            '<h1>Games that run on quantum rules</h1>'
            f'<p>{escape(data["intro"])}</p></header>'
            '<section class="game-catalog" aria-labelledby="games-heading"><div class="section-top"><div>'
            '<p class="eyebrow">Play</p><h2 id="games-heading">The games</h2></div>'
            f'<span class="game-count">{count:02} game{"" if count == 1 else "s"}</span></div>'
            f'<ol class="game-list">{"".join(game_card(n, g, "games/index.html") for n, g in enumerate(data["games"], 1))}</ol>'
            '</section>')
    shell('games/index.html', 'Quantum games',
          'Puzzles whose rules come from real quantum effects, each with an account of the physics it borrows.',
          body, assets=ASSETS)
    render_quantum_2028(shell)
