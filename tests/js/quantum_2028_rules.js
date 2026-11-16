// Rules of Quantum 2028, checked on fixed positions and on long seeded random games.
// Run: node tests/js/quantum_2028_rules.js  (tests/test_games.py runs it when Node is installed)
'use strict';
const assert = require('assert');
const path = require('path');
const {createGame, N} = require(path.join(__dirname, '../../games/quantum-2028.js'));

function seeded(seed) {  // mulberry32
  return () => {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const fixed = values => { let i = 0; return () => values[i++ % values.length]; };

/* The board as text, one row per line: '.' empty, '8' whole, '-8' minus, '8a' half of split tile a. */
function picture(game) {
  const names = new Map();
  const rows = [];
  for (let r = 0; r < N; r++) {
    const row = [];
    for (let c = 0; c < N; c++) {
      const pid = game.grid[r][c];
      if (pid == null) { row.push('.'); continue; }
      const p = game.pieces.get(pid);
      let tag = '';
      if (p.split) { if (!names.has(p.tid)) names.set(p.tid, 'abcdefgh'[names.size]); tag = names.get(p.tid); }
      row.push(`${p.s < 0 ? '-' : ''}${p.v}${tag}`);
    }
    rows.push(row.join(' '));
  }
  return rows.join('\n');
}
function board(rows) {  // the inverse of picture(), for setting up positions
  const entries = [];
  rows.forEach((line, r) => line.trim().split(/\s+/).forEach((cell, c) => {
    if (cell === '.') return;
    const m = cell.match(/^(-?)(\d+)([a-z]?)$/);
    entries.push([r, c, Number(m[2]), m[1] ? -1 : 1, m[3] || null]);
  }));
  return entries;
}
function start(rows, random = () => 0) { const g = createGame(random); g.load(board(rows)); return g; }
const same = (game, rows, message) => assert.strictEqual(picture(game), rows.map(r => r.trim().split(/\s+/).join(' ')).join('\n'), message);

/* Signed total: each tile counted once (a split tile is one tile), with its sign. Merges, cancellations,
   rejoining and measurement all conserve it; only new tiles and phase flips change it. */
function signedTotal(game) {
  const seen = new Set(); let total = 0;
  for (const p of game.pieces.values()) { if (seen.has(p.tid)) continue; seen.add(p.tid); total += p.s * p.v; }
  return total;
}
function checkConsistent(game) {
  const tiles = new Map();
  for (const [pid, p] of game.pieces) {
    assert.strictEqual(game.grid[p.r][p.c], pid, `piece ${pid} is not where the grid says`);
    if (!tiles.has(p.tid)) tiles.set(p.tid, []);
    tiles.get(p.tid).push(p);
  }
  let occupied = 0;
  for (const row of game.grid) for (const cell of row) if (cell != null) { occupied++; assert(game.pieces.has(cell), 'grid points at a missing piece'); }
  assert.strictEqual(occupied, game.pieces.size, 'grid and pieces disagree');
  for (const [tid, list] of tiles) {
    const split = list[0].split;
    assert.strictEqual(list.length, split ? 2 : 1, `tile ${tid} has ${list.length} pieces`);
    for (const p of list) assert(p.v === list[0].v && p.s === list[0].s && p.split === split, `halves of tile ${tid} disagree`);
  }
}

const tests = [];
const test = (name, fn) => tests.push([name, fn]);

test('equal tiles bunch into one tile of twice the value, split over both cells', () => {
  const g = start(['2 2 . .', '. . . .', '. . . .', '. . . .']);
  g.move('left', {spawns: false});
  same(g, ['4a 4a . .', '. . . .', '. . . .', '. . . .']);
  assert.strictEqual(g.score, 4);
});

test('each tile merges at most once per slide', () => {
  const g = start(['2 2 2 2', '2 2 4 .', '4 2 2 .', '. . . .']);
  g.move('left', {spawns: false});
  same(g, ['4a 4a 4b 4b', '4c 4c 4 .', '4 4d 4d .', '. . . .']);
});

test('the reported sequence: a split 16 rejoins, then two 2s merge and the 16 is untouched', () => {
  const g = start(['16a 16a . .', '2 . . .', '2 . . .', '. . . .']);
  g.move('left', {spawns: false});
  same(g, ['16 . . .', '2 . . .', '2 . . .', '. . . .'], 'the halves rejoin into one whole 16');
  g.move('up', {spawns: false});
  same(g, ['16 . . .', '4a . . .', '4a . . .', '. . . .'], 'the 2s become a split 4; the 16 stays a whole 16');
  assert.strictEqual(g.score, 4);
});

test('a 16 becomes a split 32 only by meeting another 16, and the log reports both merges', () => {
  const g = start(['2 2 16 16', '. . . .', '. . . .', '. . . .']);
  const out = g.move('left', {spawns: false});
  same(g, ['4a 4a 32b 32b', '. . . .', '. . . .', '. . . .']);
  assert.deepStrictEqual(out.events.filter(e => e.type === 'merge').map(e => e.v), [4, 32]);
});

test('halves of one tile rejoin across a gap, without chance', () => {
  for (const r of [0.1, 0.9]) {
    const g = start(['4a . . 4a', '. . . .', '. . . .', '. . . .'], () => r);
    g.move('left', {spawns: false});
    same(g, ['4 . . .', '. . . .', '. . . .', '. . . .']);
  }
});

test('halves in different lines drift apart and stay one tile', () => {
  const g = start(['. 4a . .', '. . 4a .', '. . . .', '. . . .']);
  g.move('left', {spawns: false});
  same(g, ['4a . . .', '4a . . .', '. . . .', '. . . .']);
  g.move('up', {spawns: false});
  same(g, ['4 . . .', '. . . .', '. . . .', '. . . .']);
});

test('contact with an equal tile measures the half first: found there, it merges', () => {
  const g = start(['8a 8 . .', '8a . . .', '. . . .', '. . . .'], fixed([0.1]));
  const out = g.move('left', {spawns: false});
  same(g, ['16a 16a . .', '. . . .', '. . . .', '. . . .']);
  assert.deepStrictEqual(out.events.map(e => e.type), ['collapse', 'merge']);
});

test('contact with an equal tile measures the half first: not found there, it vanishes', () => {
  const g = start(['8a 8 . .', '8a . . .', '. . . .', '. . . .'], fixed([0.9]));
  const out = g.move('left', {spawns: false});
  same(g, ['8 . . .', '8 . . .', '. . . .', '. . . .']);
  assert.deepStrictEqual(out.events.map(e => e.type), ['collapse']);
});

test('two split 8s meeting half to half become a split 16, whatever chance gives', () => {
  for (const r of [0.1, 0.9]) {
    const g = start(['8a 8a . .', '8b 8b . .', '. . . .', '. . . .'], () => r);
    const out = g.move('up', {spawns: false});
    same(g, ['16a 16a . .', '. . . .', '. . . .', '. . . .']);
    assert.deepStrictEqual(out.events.map(e => e.type), ['merge']);
    assert.strictEqual(g.score, 16);
  }
});

test('pairs meet half to half within one line too', () => {
  const g = start(['8a 8b 8a 8b', '. . . .', '. . . .', '. . . .']);
  g.move('left', {spawns: false});
  same(g, ['16a 16a . .', '. . . .', '. . . .', '. . . .']);
});

test('a split 8 and a split −8 meeting half to half cancel', () => {
  const g = start(['. 8a 8a .', '. -8b -8b .', '. . . .', '. . . .']);
  g.move('down', {spawns: false});
  same(g, ['. . . .', '. . . .', '. . . .', '. . . .']);
  assert.strictEqual(g.score, 0);
});

test('split tiles that meet in only one place are measured first', () => {
  const g = start(['8a 8a . .', '8b . . 8b', '. . . .', '. . . .'], fixed([0.1]));
  const out = g.move('up', {spawns: false});
  assert.strictEqual(out.events[0].type, 'collapse');
});

test('observing finds the tile in each cell about half the time', () => {
  const random = seeded(7); let first = 0; const runs = 4000;
  for (let i = 0; i < runs; i++) {
    const g = createGame(random); g.load(board(['8a . . 8a', '. . . .', '. . . .', '. . . .']));
    g.observe(g.grid[0][0]);
    if (g.grid[0][0] != null) first++;
    assert.strictEqual(g.pieces.size, 1);
  }
  assert(Math.abs(first / runs - 0.5) < 0.03, `found in the first cell ${first} of ${runs} times`);
});

test('equal tiles of opposite sign cancel and score nothing', () => {
  const g = start(['2 -2 4 .', '. . . .', '. . . .', '. . . .']);
  g.move('left', {spawns: false});
  same(g, ['4 . . .', '. . . .', '. . . .', '. . . .']);
  assert.strictEqual(g.score, 0);
});

test('minus tiles merge with each other and keep their sign', () => {
  const g = start(['-2 -2 . .', '. . . .', '. . . .', '. . . .']);
  g.move('left', {spawns: false});
  same(g, ['-4a -4a . .', '. . . .', '. . . .', '. . . .']);
});

test('a phase flip changes the sign of both halves and spends one flip', () => {
  const g = start(['4a 4a . .', '. . . .', '. . . .', '. . . .']);
  const flips = g.flips;
  g.flip(g.grid[0][1]);
  same(g, ['-4a -4a . .', '. . . .', '. . . .', '. . . .']);
  assert.strictEqual(g.flips, flips - 1);
});

test('a slide that changes nothing is not a move', () => {
  const g = start(['2 4 . .', '. . . .', '. . . .', '. . . .']);
  assert.strictEqual(g.move('left').changed, false);
  same(g, ['2 4 . .', '. . . .', '. . . .', '. . . .'], 'no tile is added');
});

test('the game ends only when no slide works and nothing is split', () => {
  const full = ['2 4 2 4', '4 2 4 2', '2 4 2 4', '4 2 4 8'];
  const g = start(full);
  assert.strictEqual(g.stuck(), true);
  const h = start(['2 4 2 4', '4 2 4 2', '2 4 2 4', '4 2 8a 8a']);
  assert.strictEqual(h.stuck(), false, 'a split tile can still be observed or rejoined');
});

test('a full board with a split tile asks for an observation instead of ending', () => {
  // Sliding right fills the bottom row; the new tile (a plus 2, from random 0.99) lands in the gap.
  const g = start(['4 2 4 2', '2 4 2 4', '4 2 4 2', '16a 8 . 16a'], () => 0.99);
  const out = g.move('right');
  same(g, ['4 2 4 2', '2 4 2 4', '4 2 4 2', '2 16a 8 16a']);
  assert.strictEqual(g.over, false);
  assert(out.events.some(e => e.type === 'blocked'), 'the player is told to observe');
});

test('long random games keep every invariant', () => {
  const random = seeded(2028);
  let moves = 0, games = 0, biggest = 0;
  for (; games < 300; games++) {
    const g = createGame(random); g.reset();
    const values = new Map();
    for (let i = 0; i < 3000 && !g.over; i++) {
      const before = signedTotal(g), pidsBefore = new Set(g.pieces.keys());
      let out;
      const roll = random();
      if (roll < 0.08) {
        const split = [...g.pieces.values()].filter(p => p.split);
        if (!split.length) continue;
        out = g.observe(split[Math.floor(random() * split.length)].pid);
      } else {
        out = g.move(['left', 'right', 'up', 'down'][Math.floor(random() * 4)]);
        moves++;
      }
      checkConsistent(g);
      const added = out.born.filter(pid => !pidsBefore.has(pid)).map(pid => g.pieces.get(pid))
        .filter(p => p && !p.split).reduce((sum, p) => sum + p.s * p.v, 0);
      assert.strictEqual(signedTotal(g), before + added, `signed total changed outside a new tile (game ${games}, move ${i})`);
      for (const p of g.pieces.values()) {
        if (values.has(p.pid)) assert.strictEqual(values.get(p.pid), p.v * p.s, `piece ${p.pid} changed value`);
        values.set(p.pid, p.v * p.s);
        biggest = Math.max(biggest, p.v);
      }
    }
  }
  assert(moves > 50000, `only ${moves} moves`);
  return `${games} games, ${moves} moves, largest tile ${biggest}`;
});

let failed = 0;
for (const [name, fn] of tests) {
  try { const note = fn(); console.log(`ok   ${name}${note ? ` (${note})` : ''}`); }
  catch (error) { failed++; console.log(`FAIL ${name}\n     ${error.message.split('\n').join('\n     ')}`); }
}
console.log(failed ? `${failed} of ${tests.length} failed` : `all ${tests.length} passed`);
process.exit(failed ? 1 : 0);
