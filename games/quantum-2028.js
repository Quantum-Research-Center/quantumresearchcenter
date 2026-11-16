/* Quantum 2028: a sliding-merge puzzle on quantum rules.
   Two equal tiles with the same sign bunch into one tile of twice the value, held in both of their cells
   at once (the Hong–Ou–Mandel effect). Observation, or contact with an equal tile, finds it in one cell
   with probability 1/2, except that two equal split tiles whose halves meet pairwise in one slide
   combine into a split tile of twice the value without being observed. Equal tiles of opposite sign
   cancel. The two halves of one tile rejoin on contact.

   The rules live in createGame(), which touches no page and takes its random numbers as a parameter, so
   tests can replay exact positions. The page code below it only draws the state and reports events. */
(() => {
  'use strict';
  const N = 4;
  const RULES = {minusChance: 0.2, fourChance: 0.1, mergesPerFlip: 8, startFlips: 2, maxFlips: 9, goal: 2048};
  const DIRECTIONS = ['left', 'right', 'up', 'down'];

  /* A piece is one occupied cell. A whole tile is one piece; a split tile is two pieces sharing a tile id
     (tid). Values and signs belong to the tile, so both halves always carry the same ones. */
  function createGame(random = Math.random, rules = RULES) {
    const game = {pieces: new Map(), grid: [], nextId: 1, score: 0, merges: 0, flips: rules.startFlips, over: false, won: false};
    const empty = () => Array.from({length: N}, () => Array(N).fill(null));

    function make(r, c, v, s, tid, split) {
      const pid = game.nextId++;
      return {pid, tid: tid ?? pid, v, s, split: !!split, r, c};
    }
    function put(piece) { game.pieces.set(piece.pid, piece); game.grid[piece.r][piece.c] = piece.pid; }
    const at = (r, c) => (game.grid[r][c] == null ? null : game.pieces.get(game.grid[r][c]));
    const halves = tid => [...game.pieces.values()].filter(p => p.tid === tid);

    /* Cells of each line, front first, for a slide in direction dir. */
    function lines(dir) {
      const out = [];
      for (let i = 0; i < N; i++) {
        const line = [];
        for (let j = 0; j < N; j++) {
          if (dir === 'left') line.push([i, j]);
          else if (dir === 'right') line.push([i, N - 1 - j]);
          else if (dir === 'up') line.push([j, i]);
          else line.push([N - 1 - j, i]);
        }
        out.push(line);
      }
      return out;
    }

    /* Work out a slide without changing anything. Returns {collapse: tid} when a half must be measured
       first, otherwise the actions and whether the board would change. Each tile acts at most once. */
    function plan(dir) {
      const actions = [];
      const meetings = new Map();  // two split tiles of equal value -> the places where their halves meet
      let changed = false;
      for (const cells of lines(dir)) {
        const list = cells.map(([r, c]) => at(r, c)).filter(Boolean);
        let slot = 0;
        for (let i = 0; i < list.length;) {
          const p = list[i], q = list[i + 1];
          if (q && p.tid === q.tid) {
            actions.push({kind: 'rejoin', keep: p, drop: q, to: cells[slot]});
            slot += 1; i += 2; changed = true; continue;
          }
          if (q && p.v === q.v) {
            if (p.split && q.split) {
              const key = Math.min(p.tid, q.tid) + ':' + Math.max(p.tid, q.tid);
              if (!meetings.has(key)) meetings.set(key, []);
              meetings.get(key).push({p, q, cell: cells[slot]});
              slot += 1; i += 2; changed = true; continue;
            }
            if (p.split || q.split) return {collapse: p.split ? p.tid : q.tid};
            const to = [cells[slot], cells[slot + 1]];
            if (p.s === q.s) {
              actions.push({kind: 'merge', from: [p, q], fold: to, to, v: p.v * 2, s: p.s});
              slot += 2;
            } else {
              actions.push({kind: 'cancel', from: [p, q], fold: [to[0], to[0]], v: p.v});
            }
            i += 2; changed = true; continue;
          }
          const to = cells[slot];
          if (to[0] !== p.r || to[1] !== p.c) changed = true;
          actions.push({kind: 'slide', piece: p, to});
          slot += 1; i += 1;
        }
      }
      /* Two split tiles combine without measurement only when both halves of one meet both halves of the
         other: the result is again split, over the two meeting places. A lone meeting is a measurement. */
      for (const met of meetings.values()) {
        if (met.length !== 2) return {collapse: met[0].p.tid};
        const [a, b] = met, from = [a.p, a.q, b.p, b.q], fold = [a.cell, a.cell, b.cell, b.cell];
        if (a.p.s === a.q.s) actions.push({kind: 'merge', from, fold, to: [a.cell, b.cell], v: a.p.v * 2, s: a.p.s});
        else actions.push({kind: 'cancel', from, fold, v: a.p.v});
      }
      return {actions, changed};
    }

    /* Measure a split tile: one half survives, each with probability 1/2. */
    function collapse(tid, cause, out) {
      const pair = halves(tid);
      if (pair.length !== 2) throw new Error(`tile ${tid} has ${pair.length} halves`);
      const keep = pair[random() < 0.5 ? 0 : 1], drop = pair[0] === keep ? pair[1] : pair[0];
      keep.split = false;
      game.grid[drop.r][drop.c] = null;
      game.pieces.delete(drop.pid);
      out.gone.push({pid: drop.pid, to: [drop.r, drop.c], how: 'vanish'});
      out.events.push({type: 'collapse', cause, v: keep.v, s: keep.s, at: [keep.r, keep.c], emptied: [drop.r, drop.c]});
    }

    function apply(actions, out) {
      game.grid = empty();
      const born = [];
      for (const a of actions) {
        if (a.kind === 'slide') { a.piece.r = a.to[0]; a.piece.c = a.to[1]; }
        else if (a.kind === 'rejoin') {
          a.keep.r = a.to[0]; a.keep.c = a.to[1]; a.keep.split = false;
          game.pieces.delete(a.drop.pid);
          out.gone.push({pid: a.drop.pid, to: a.to, how: 'fold'});
          out.events.push({type: 'rejoin', v: a.keep.v, s: a.keep.s, at: a.to});
        } else if (a.kind === 'cancel') {
          a.from.forEach((p, k) => { game.pieces.delete(p.pid); out.gone.push({pid: p.pid, to: a.fold[k], how: 'vanish'}); });
          out.events.push({type: 'cancel', v: a.v, split: a.from.length > 2});
        } else {
          a.from.forEach((p, k) => { game.pieces.delete(p.pid); out.gone.push({pid: p.pid, to: a.fold[k], how: 'fold'}); });
          const tid = game.nextId;
          for (const [r, c] of a.to) born.push(make(r, c, a.v, a.s, tid, true));
          game.score += a.v; game.merges += 1;
          out.events.push({type: 'merge', from: a.from[0].v, v: a.v, s: a.s, cells: a.to, split: a.from.length > 2});
          if (game.merges % rules.mergesPerFlip === 0 && game.flips < rules.maxFlips) {
            game.flips += 1; out.events.push({type: 'flip-earned', merges: game.merges});
          }
          if (a.v >= rules.goal && !game.won) { game.won = true; out.events.push({type: 'won', v: a.v}); }
        }
      }
      for (const p of game.pieces.values()) {
        if (game.grid[p.r][p.c] != null) throw new Error(`two pieces in row ${p.r + 1}, column ${p.c + 1}`);
        game.grid[p.r][p.c] = p.pid;
      }
      for (const h of born) put(h);
      out.born.push(...born.map(h => h.pid));
    }

    function spawn(out) {
      const free = [];
      for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) if (game.grid[r][c] == null) free.push([r, c]);
      if (!free.length) return;
      const [r, c] = free[Math.floor(random() * free.length)];
      const piece = make(r, c, random() < rules.fourChance ? 4 : 2, random() < rules.minusChance ? -1 : 1);
      put(piece);
      out.born.push(piece.pid);
    }

    const canSlide = () => DIRECTIONS.some(dir => { const p = plan(dir); return p.collapse != null || p.changed; });
    const stuck = () => ![...game.pieces.values()].some(p => p.split) && !canSlide();

    const result = () => ({changed: false, events: [], gone: [], born: []});
    function finish(out) {
      if (out.changed && !game.over && !canSlide()) {
        // With a split tile left, observing it frees a cell, so the game goes on; otherwise it is over.
        if (stuck()) { game.over = true; out.events.push({type: 'over', score: game.score}); }
        else out.events.push({type: 'blocked'});
      }
      return out;
    }

    game.reset = () => {
      game.pieces = new Map(); game.grid = empty(); game.nextId = 1; game.score = 0; game.merges = 0;
      game.flips = rules.startFlips; game.over = false; game.won = false;
      const out = result(); spawn(out); spawn(out); return out;
    };
    /* Place tiles directly, for tests: each entry is [row, column, value, sign, tile id or null]. Entries
       that share a tile id are the two halves of one split tile. */
    game.load = entries => {
      game.pieces = new Map(); game.grid = empty(); game.over = false;
      const ids = new Map();
      for (const [r, c, v, s, tag] of entries) {
        const tid = tag == null ? undefined : (ids.get(tag) ?? game.nextId);
        const piece = make(r, c, v, s, tid, tag != null);
        if (tag != null) ids.set(tag, piece.tid);
        put(piece);
      }
    };
    game.plan = plan;
    game.stuck = stuck;
    game.halves = halves;
    game.move = (dir, {spawns = true} = {}) => {
      const out = result();
      if (game.over) return out;
      for (let guard = 0; ; guard++) {
        const p = plan(dir);
        if (p.collapse != null) {
          if (guard > 2 * N * N) throw new Error('contact measurement did not settle');
          collapse(p.collapse, 'contact', out); out.changed = true; continue;
        }
        if (p.changed) { apply(p.actions, out); out.changed = true; }
        break;
      }
      if (out.changed && spawns) spawn(out);
      return finish(out);
    };
    game.observe = pid => {
      const out = result(), p = game.pieces.get(pid);
      if (!p || !p.split || game.over) return out;
      collapse(p.tid, 'observed', out); out.changed = true;
      return finish(out);
    };
    game.flip = pid => {
      const out = result(), p = game.pieces.get(pid);
      if (!p || game.flips < 1 || game.over) return out;
      for (const h of halves(p.tid)) h.s = -h.s;
      game.flips -= 1; out.changed = true;
      out.events.push({type: 'flip', v: p.v, s: p.s, at: [p.r, p.c]});
      return finish(out);
    };
    game.grid = empty();
    return game;
  }

  if (typeof module === 'object' && module.exports) module.exports = {createGame, RULES, N};
  if (typeof document === 'undefined') return;

  /* ---- The page ---- */
  const GAP = 3, CELL = (100 - (N + 1) * GAP) / N, STEP = CELL + GAP, BEST_KEY = 'qrc-quantum-2028-best';
  const KEYS = {ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down',
                a: 'left', d: 'right', w: 'up', s: 'down', A: 'left', D: 'right', W: 'up', S: 'down'};
  const board = document.getElementById('bunch-board');
  if (!board) return;
  const layer = document.getElementById('bunch-pieces');
  const links = document.getElementById('bunch-links');
  const scoreOut = document.getElementById('bunch-score');
  const bestOut = document.getElementById('bunch-best');
  const flipsOut = document.getElementById('bunch-flips');
  const flipButton = document.getElementById('bunch-flip');
  const newButton = document.getElementById('bunch-new');
  const status = document.getElementById('bunch-status');
  const log = document.getElementById('bunch-log');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  const game = createGame();
  let flipMode = false;
  const read = key => { try { return window.localStorage.getItem(key); } catch { return null; } };
  const write = (key, value) => { try { window.localStorage.setItem(key, value); } catch { /* storage unavailable */ } };
  let best = Number(read(BEST_KEY)) || 0;

  const where = ([r, c]) => `row ${r + 1}, column ${c + 1}`;
  const signWord = s => (s > 0 ? 'plus' : 'minus');
  const named = (v, s) => `${s > 0 ? '' : '−'}${v}`;
  const an = v => (String(v).startsWith('8') ? 'an' : 'a');
  const capital = text => text[0].toUpperCase() + text.slice(1);

  function describe(e) {
    switch (e.type) {
      case 'collapse': return `${e.cause === 'contact' ? 'Contact observed a split tile' : 'You observed a split tile'}: the ${named(e.v, e.s)} was found at ${where(e.at)}; ${where(e.emptied)} is empty.`;
      case 'rejoin': return `The two halves of the ${named(e.v, e.s)} rejoined at ${where(e.at)}.`;
      case 'cancel': return e.split ? `A split ${e.v} and a split −${e.v} met half to half and cancelled.`
        : `${capital(an(e.v))} ${e.v} and a −${e.v} cancelled.`;
      case 'merge': return `Two ${e.split ? 'split ' : ''}${named(e.from, e.s)}s bunched into ${an(e.v)} ${named(e.v, e.s)}, split between ${where(e.cells[0])} and ${where(e.cells[1])}.`;
      case 'flip-earned': return `Merge ${e.merges}: you earned a phase flip.`;
      case 'won': return `You made ${an(e.v)} ${e.v}. Keep going if you like.`;
      case 'flip': return `Phase flip: the tile at ${where(e.at)} is now ${signWord(e.s)} ${e.v}.`;
      case 'blocked': return 'No slide can move anything now. Observe a split tile to free a cell.';
      case 'over': return `No move changes the board and nothing is left to observe. Final score ${e.score}.`;
      default: return '';
    }
  }
  function report(out) {
    // Every event of the turn goes in the log, oldest first, so a turn with several merges reads in full.
    for (const e of out.events) {
      const text = describe(e);
      if (!text) continue;
      const item = document.createElement('li');
      item.textContent = text;
      log.prepend(item);
      status.textContent = text;
    }
    while (log.children.length > 8) log.lastChild.remove();
  }

  const left = c => GAP + c * STEP;
  const centre = n => GAP + n * STEP + CELL / 2;
  const shade = p => Math.min(14 + Math.log2(p.v) * 7.5, 92) * (p.split ? 0.6 : 1);

  function render(out) {
    const born = new Set(out ? out.born : []);
    const keep = new Set();
    for (const p of game.pieces.values()) {
      keep.add(String(p.pid));
      let el = layer.querySelector(`[data-pid="${p.pid}"]`);
      if (!el) {
        el = document.createElement('button');
        el.type = 'button';
        el.className = 'bunch-piece';
        el.dataset.pid = p.pid;
        el.innerHTML = '<span class="bunch-sign" aria-hidden="true"></span><span class="bunch-value"></span><span class="bunch-prob" aria-hidden="true">½</span>';
        layer.append(el);
        if (born.has(p.pid) && !reduced.matches) el.classList.add(p.split ? 'is-born' : 'is-new');
      }
      el.dataset.tid = p.tid;
      const mix = shade(p);
      el.style.left = `${left(p.c)}%`;
      el.style.top = `${left(p.r)}%`;
      el.style.setProperty('--mix', `${mix}%`);
      el.classList.toggle('is-minus', p.s < 0);
      el.classList.toggle('is-split', p.split);
      el.classList.toggle('is-dark', mix > 52);
      el.classList.toggle('is-long', p.v >= 1024);
      el.querySelector('.bunch-sign').textContent = p.s > 0 ? '+' : '−';
      el.querySelector('.bunch-value').textContent = p.v;
      el.tabIndex = !game.over && (flipMode || p.split) ? 0 : -1;
      el.setAttribute('aria-label', `${signWord(p.s)} ${p.v} at ${where([p.r, p.c])}` +
        (p.split ? ', split: found here with probability one half. Press to observe.' : '') +
        (flipMode ? '. Press to flip its sign.' : ''));
    }
    for (const gone of out ? out.gone : []) {
      const el = layer.querySelector(`[data-pid="${gone.pid}"]`);
      if (!el) continue;
      if (el.contains(document.activeElement)) board.focus({preventScroll: true});  // keep the keys alive
      el.dataset.pid = '';
      el.tabIndex = -1;
      el.style.left = `${left(gone.to[1])}%`;
      el.style.top = `${left(gone.to[0])}%`;
      el.classList.add(gone.how === 'fold' ? 'is-folding' : 'is-vanishing');
      setTimeout(() => el.remove(), reduced.matches ? 0 : 220);
    }
    for (const el of layer.querySelectorAll('.bunch-piece')) if (el.dataset.pid && !keep.has(el.dataset.pid)) el.remove();
    links.innerHTML = '';
    const seen = new Set();
    for (const p of game.pieces.values()) {
      if (!p.split || seen.has(p.tid)) continue;
      seen.add(p.tid);
      const [a, b] = game.halves(p.tid);
      if (!b) continue;
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', centre(a.c)); line.setAttribute('y1', centre(a.r));
      line.setAttribute('x2', centre(b.c)); line.setAttribute('y2', centre(b.r));
      line.setAttribute('class', p.s > 0 ? 'bunch-link' : 'bunch-link is-minus');
      line.setAttribute('vector-effect', 'non-scaling-stroke');
      links.append(line);
    }
    if (game.score > best) { best = game.score; write(BEST_KEY, String(best)); }
    scoreOut.textContent = game.score;
    bestOut.textContent = best;
    flipsOut.textContent = game.flips;
    flipButton.disabled = game.flips < 1 || game.over;
    board.classList.toggle('is-over', game.over);
  }

  function turn(out) { if (!out.changed) return; report(out); render(out); }

  function setFlipMode(on) {
    flipMode = on && game.flips > 0 && !game.over;
    board.classList.toggle('is-flipping', flipMode);
    flipButton.setAttribute('aria-pressed', String(flipMode));
    if (flipMode) status.textContent = 'Choose a tile to flip its sign.';
    render();
  }

  function tap(pid) {
    if (flipMode) { setFlipMode(false); turn(game.flip(pid)); }
    else turn(game.observe(pid));
  }

  function reset() {
    layer.innerHTML = '';
    log.innerHTML = '';
    const out = game.reset();
    setFlipMode(false);
    status.textContent = 'Slide with the arrow keys, WASD or a swipe.';
    render(out);
  }

  /* Input: keys while the game has focus, swipes and taps by pointer. Once the player has used the board,
     keys keep driving it until they move focus to something else on the page. */
  let engaged = false;
  board.addEventListener('focusin', () => { engaged = true; });
  document.addEventListener('focusin', event => {
    if (!board.contains(event.target) && event.target !== newButton && event.target !== flipButton) engaged = false;
  });
  document.addEventListener('keydown', event => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return;
    const active = document.activeElement;
    const inGame = board.contains(active) || (engaged && (!active || active === document.body || active === newButton || active === flipButton));
    if (!inGame) return;
    const dir = KEYS[event.key];
    if (dir) { event.preventDefault(); turn(game.move(dir)); }
    else if (event.key === 'Escape' && flipMode) setFlipMode(false);
  });
  let start = null;
  board.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    start = {x: event.clientX, y: event.clientY, target: event.target.closest('.bunch-piece')};
    // Keep focus on the board itself, not on a tile that the next move may remove.
    event.preventDefault();
    board.focus({preventScroll: true});
  });
  board.addEventListener('pointerup', event => {
    if (!start) return;
    const dx = event.clientX - start.x, dy = event.clientY - start.y, target = start.target;
    start = null;
    if (Math.max(Math.abs(dx), Math.abs(dy)) >= 24) {
      turn(game.move(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up')));
    } else if (target && target.dataset.pid) {
      tap(Number(target.dataset.pid));
    }
  });
  board.addEventListener('pointercancel', () => { start = null; });
  layer.addEventListener('click', event => {
    // Keyboard activation of a focused tile (pointer taps are handled on pointerup).
    if (event.detail !== 0) return;
    const target = event.target.closest('.bunch-piece');
    if (target && target.dataset.pid) tap(Number(target.dataset.pid));
  });
  flipButton.addEventListener('click', () => setFlipMode(!flipMode));
  newButton.addEventListener('click', () => { reset(); board.focus({preventScroll: true}); });

  board.hidden = false;
  document.getElementById('bunch-panel').hidden = false;
  reset();
})();
