"""Draw the figures for the NPT bound entanglement article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
Labels carrying data-tex are typeset by MathJax on the page; the plain text is the fallback.
"""
import math
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent


def svg(width, height, body):
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{body}</svg>\n'


def text(x, y, s, cls='fig-text', anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def tex(x, y, plain, latex, cls='fig-label', anchor='start'):
    return text(x, y, plain, cls, anchor, f' data-tex="{escape(latex)}"')


def path(points, cls):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)
    return f'<path d="{d}" class="{cls}"/>'


def arrow(x1, y1, x2, y2, cls='fig-link', head=8):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.45), y2 - head * math.sin(a - 0.45))
    p2 = (x2 - head * math.cos(a + 0.45), y2 - head * math.sin(a + 0.45))
    return path([(x1, y1), (x2, y2)], cls) + path([p1, (x2, y2), p2], cls)


def distill():
    """Many noisy pairs in, fewer good pairs out, by local operations and classical communication."""
    W, H = 640, 250
    out = []
    for k in range(6):
        y = 40 + k * 32
        out.append(f'<circle cx="60" cy="{y}" r="7" class="fig-node"/><circle cx="170" cy="{y}" r="7" class="fig-node"/>')
        out.append(path([(67, y), (163, y)], 'fig-ref'))
    out.append(text(115, 18, 'many noisy pairs', 'fig-muted', 'middle'))
    out.append(f'<rect x="215" y="40" width="210" height="160" rx="6" class="fig-box"/>')
    out.append(text(320, 100, 'local operations and', 'fig-text', 'middle'))
    out.append(text(320, 120, 'classical communication', 'fig-text', 'middle'))
    out.append(text(320, 150, 'Alice ⟷ Bob', 'fig-muted', 'middle'))
    out.append(arrow(180, 120, 210, 120, 'fig-link'))
    out.append(arrow(430, 120, 460, 120, 'fig-link'))
    for k in range(2):
        y = 95 + k * 50
        out.append(f'<circle cx="490" cy="{y}" r="7" class="fig-fill-1"/><circle cx="600" cy="{y}" r="7" class="fig-fill-1"/>')
        out.append(path([(497, y), (593, y)], 'fig-line-1'))
    out.append(text(545, 70, 'fewer near-perfect', 'fig-muted', 'middle'))
    out.append(text(545, 200, 'Bell pairs', 'fig-muted', 'middle'))
    out.append(text(320, 236, 'bound entangled: entangled, yet the right-hand side stays empty', 'fig-label', 'middle'))
    return svg(W, H, ''.join(out))


def werner_line():
    """The Werner family (I - a SWAP)/(d^2 - a d) for d = 8, with the regions known before and the new point."""
    W, H = 640, 220
    x0, x1, y = 50, 600, 120
    X = lambda a: x0 + (a + 1) / 2 * (x1 - x0)
    out = [f'<rect x="{X(-1):.1f}" y="{y - 14}" width="{X(1 / 8) - X(-1):.1f}" height="28" class="fig-fill-muted-soft"/>',
           f'<rect x="{X(1 / 8):.1f}" y="{y - 14}" width="{X(0.5) - X(1 / 8):.1f}" height="28" class="fig-wash-2"/>',
           f'<rect x="{X(0.5):.1f}" y="{y - 14}" width="{X(1) - X(0.5):.1f}" height="28" class="fig-wash-1"/>',
           path([(x0, y), (x1, y)], 'fig-axis')]
    for a, lab, latex in ((-1, '−1', '-1'), (0, '0', '0'), (1 / 8, '1/8', r'\tfrac18'), (0.5, '1/2', r'\tfrac12'), (1, '1', '1')):
        out.append(path([(X(a), y + 14), (X(a), y + 22)], 'fig-axis'))
        out.append(tex(X(a), y + 40, lab, latex, 'fig-muted', 'middle'))
    out.append(text((X(-1) + X(1 / 8)) / 2, y - 24, 'separable (PPT)', 'fig-text', 'middle'))
    out.append(text((X(1 / 8) + X(0.5)) / 2, y - 40, 'NPT,', 'fig-text', 'middle'))
    out.append(text((X(1 / 8) + X(0.5)) / 2, y - 24, 'conjectured bound', 'fig-text', 'middle'))
    out.append(text((X(0.5) + X(1)) / 2, y - 24, 'distillable', 'fig-text', 'middle'))
    xa = X(3 / 23)
    out.append(f'<circle cx="{xa:.1f}" cy="{y}" r="6" class="fig-fill-2"/>')
    out.append(path([(xa, y + 8), (xa + 24, y + 52)], 'fig-link'))
    out.append(tex(xa + 28, y + 66, 'the new state, a = 3/23', r'\text{the new state, } \alpha=3/23\approx0.130', 'fig-label'))
    out.append(tex((x0 + x1) / 2, H + 10, 'Werner parameter a', r'\text{Werner parameter } \alpha \text{ in } (I-\alpha\,\mathrm{SWAP})/(64-8\alpha)', 'fig-muted', 'middle'))
    return svg(W, H + 20, ''.join(out))


if __name__ == '__main__':
    for name, draw in (('distill.svg', distill), ('werner.svg', werner_line)):
        (HERE / name).write_text(draw())
        print('wrote', name)
