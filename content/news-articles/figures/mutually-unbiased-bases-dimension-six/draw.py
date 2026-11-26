"""Draw the figures for the mutually unbiased bases article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
Labels carrying data-tex are typeset by MathJax on the page; the plain text is the fallback.
"""
import math
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Largest known number of mutually unbiased bases N(d) for d = 2..12, and the upper bound d + 1.
# Prime powers attain d + 1 (Wootters and Fields); d = 6 is now settled at 3; d = 10 has the tensor-product
# lower bound 3; d = 12 has 5 from Cárdenes Wuttig and Tindall (arXiv:2609.40311).
KNOWN = {2: 3, 3: 4, 4: 5, 5: 6, 6: 3, 7: 8, 8: 9, 9: 10, 10: 3, 11: 12, 12: 5}
SETTLED = {2, 3, 4, 5, 6, 7, 8, 9, 11}


def svg(width, height, body):
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{body}</svg>\n'


def text(x, y, s, cls='fig-text', anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def tex(x, y, plain, latex, cls='fig-label', anchor='start'):
    return text(x, y, plain, cls, anchor, f' data-tex="{escape(latex)}"')


def path(points, cls, title=None):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)
    tip = f'<title>{escape(title)}</title>' if title else ''
    return f'<path d="{d}" class="{cls}">{tip}</path>'


def bloch():
    """A qubit's three mutually unbiased bases are the three axis pairs of the Bloch sphere."""
    W, H = 640, 300
    cx, cy, r = 190, 150, 115
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" class="fig-box"/>',
           f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 0.32:.1f}" class="fig-grid"/>']
    # projected axes: z vertical, x toward viewer-left, y to the right
    axes = {'z': (0, -1), 'x': (-0.55, 0.42), 'y': (1, 0)}
    cls = {'z': 'fig-line-1', 'x': 'fig-line-2', 'y': 'fig-measure'}
    names = {'z': ('|0⟩', '|1⟩', r'\ket{0}', r'\ket{1}'), 'x': ('|+⟩', '|−⟩', r'\ket{+}', r'\ket{-}'),
             'y': ('|+i⟩', '|−i⟩', r'\ket{+i}', r'\ket{-i}')}
    for k, (dx, dy) in axes.items():
        a, b = (cx + r * dx, cy + r * dy), (cx - r * dx, cy - r * dy)
        out.append(path([a, b], cls[k]))
        for (px, py), plain, latex, sgn in ((a, names[k][0], names[k][2], 1), (b, names[k][1], names[k][3], -1)):
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" class="fig-fill-1"/>')
            out.append(tex(px + 16 * sgn * dx + (8 if k == 'z' else 0), py + 16 * sgn * dy + 5, plain, latex, 'fig-label', 'middle'))
    x0 = 360
    out.append(text(x0, 70, 'Three bases, one per axis.', 'fig-label'))
    out.append(text(x0, 96, 'States on one axis are orthogonal;', 'fig-text'))
    out.append(text(x0, 116, 'states on different axes overlap', 'fig-text'))
    out.append(tex(x0, 136, 'with probability exactly 1/2.', r'\text{with probability exactly } \tfrac12.', 'fig-text'))
    out.append(text(x0, 176, 'A qubit has room for exactly', 'fig-text'))
    out.append(tex(x0, 196, 'd + 1 = 3 such bases.', r'd+1=3 \text{ such bases.}', 'fig-text'))
    return svg(W, H, ''.join(out))


def counts():
    """Largest known number of mutually unbiased bases in dimensions 2 to 12, against the bound d + 1."""
    W, H = 640, 320
    x0, x1, y0, y1 = 56, 620, 270, 20
    bw = (x1 - x0) / 11
    Y = lambda n: y0 - n / 13 * (y0 - y1)
    out = []
    for n in (0, 4, 8, 12):
        out.append(f'<path d="M{x0},{Y(n):.1f} H{x1}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(n) + 4, str(n), 'fig-muted', 'end'))
    for i, d in enumerate(range(2, 13)):
        x = x0 + i * bw + 6
        w = bw - 12
        out.append(f'<rect x="{x:.1f}" y="{Y(d + 1):.1f}" width="{w:.1f}" height="{Y(0) - Y(d + 1):.1f}" class="fig-box-open"><title>Upper bound d + 1 = {d + 1}</title></rect>')
        cls = 'fig-fill-1' if d in SETTLED else 'fig-fill-muted'
        if d == 6:
            cls = 'fig-fill-2'
        state = 'settled' if d in SETTLED else 'best known lower bound'
        out.append(f'<rect x="{x:.1f}" y="{Y(KNOWN[d]):.1f}" width="{w:.1f}" height="{Y(0) - Y(KNOWN[d]):.1f}" class="{cls}"><title>d = {d}: {KNOWN[d]} ({state})</title></rect>')
        out.append(text(x + w / 2, Y(KNOWN[d]) - 6, str(KNOWN[d]), 'fig-label', 'middle'))
        out.append(text(x + w / 2, y0 + 18, str(d), 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    out.append(tex((x0 + x1) / 2, H - 8, 'dimension d', r'\text{dimension } d', 'fig-muted', 'middle'))
    return svg(W, H, ''.join(out))


if __name__ == '__main__':
    for name, draw in (('bloch.svg', bloch), ('counts.svg', counts)):
        (HERE / name).write_text(draw())
        print('wrote', name)
