"""Draw the figures for the quartic query separation article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
Labels carrying data-tex are typeset by MathJax on the page; the plain text is the fallback.
"""
import math
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Best exponent a with R(f) >= Q(f)^(a - o(1)) for some total function, and the best universal upper bound.
LOWER = [(1996, 2.0, 'Grover'), (2016, 2.5, 'cheat sheets'), (2020, 8 / 3, 'Tal'), (2021, 3.0, 'Bansal–Sinha; Sherstov–Storozhenko–Wu')]
UPPER = [(1998, 6.0, 'Beals et al.'), (2020, 4.0, 'Aaronson et al., via Huang')]


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


def arrow(x1, y1, x2, y2, cls='fig-link', head=7):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.45), y2 - head * math.sin(a - 0.45))
    p2 = (x2 - head * math.cos(a + 0.45), y2 - head * math.sin(a + 0.45))
    return path([(x1, y1), (x2, y2)], cls) + path([p1, (x2, y2), p2], cls)


def ladder():
    """The exponent gap for total functions over time: separations from below, universal bounds from above."""
    W, H = 640, 330
    x0, x1, y0, y1 = 56, 600, 280, 20
    X = lambda yr: x0 + (yr - 1994) / (2028 - 1994) * (x1 - x0)
    Y = lambda a: y0 - (a - 1.5) / (6.5 - 1.5) * (y0 - y1)
    out = []
    for a in (2, 3, 4, 5, 6):
        out.append(f'<path d="M{x0},{Y(a):.1f} H{x1}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(a) + 4, str(a), 'fig-muted', 'end'))
    for yr in (2000, 2010, 2020):
        out.append(text(X(yr), y0 + 18, str(yr), 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    pts, prev = [], None
    for yr, a, _ in LOWER:
        if prev is not None:
            pts.append((X(yr), Y(prev)))
        pts.append((X(yr), Y(a)))
        prev = a
    pts.append((X(2026.75), Y(prev)))
    out.append(path(pts, 'fig-line-1', 'Best separation exponent known'))
    for yr, a, name in LOWER:
        out.append(f'<circle cx="{X(yr):.1f}" cy="{Y(a):.1f}" r="4" class="fig-fill-1"><title>{yr}: {a:.3g} ({name})</title></circle>')
    out.append(path([(X(2026.75), Y(3)), (X(2026.75), Y(4))], 'fig-ref', 'Claimed: every exponent below 4'))
    out.append(f'<circle cx="{X(2026.75):.1f}" cy="{Y(4):.1f}" r="5" class="fig-hollow"><title>OpenAI, October 2026: exponent 4 - o(1) claimed</title></circle>')
    pts, prev = [], None
    for yr, a, _ in UPPER:
        if prev is not None:
            pts.append((X(yr), Y(prev)))
        pts.append((X(yr), Y(a)))
        prev = a
    pts.append((X(2028), Y(prev)))
    out.append(path(pts, 'fig-line-2', 'Best universal upper bound'))
    out.append(path([(X(2020), Y(3)), (X(2026.5), Y(3))], 'fig-measure', 'Conjectured in 2020: R = O(Q^3)'))
    out.append(text(X(1996) + 6, Y(2) - 8, 'Grover: 2', 'fig-text'))
    out.append(text(X(2016) - 6, Y(2.5) - 8, 'cheat sheets: 2.5', 'fig-text', 'end'))
    out.append(text(X(2021) - 6, Y(3) - 10, 'cubic: 3', 'fig-text', 'end'))
    out.append(text(X(1999), Y(6) - 8, 'upper bound: 6 (1998)', 'fig-label'))
    out.append(text(X(2020) - 6, Y(4) - 8, 'upper bound: 4 (2020)', 'fig-label', 'end'))
    out.append(text(X(2026.75) - 8, Y(3.55), 'claimed', 'fig-muted', 'end'))
    out.append(text(X(2026.75) - 8, Y(3.55) + 14, 'Oct 2026', 'fig-muted', 'end'))
    out.append(text(X(2021) + 4, Y(3) + 16, 'conjectured limit', 'fig-muted'))
    out.append(tex(14, (y0 + y1) / 2, 'exponent', r'\alpha', 'fig-label', 'middle'))
    out.append(text((x0 + x1) / 2, H - 8, 'separations R ≈ Q^α (blue) and universal bounds R = O(Q^α) (orange)', 'fig-muted', 'middle',
                    f' data-tex="{escape(r"\text{separations } R\approx Q^{\alpha} \text{ (blue) and bounds } R=O(Q^{\alpha}) \text{ (orange)}")}"'))
    return svg(W, H, ''.join(out))


def construction():
    """Columns, each a string of bits and a certificate; the winner's string is all ones and its pointers hit zeros."""
    W, H = 640, 300
    out = []
    cols = 5
    win = 2
    zero_rows = {0: 3, 1: 6, 3: 1, 4: 4}
    cx = [90 + 115 * i for i in range(cols)]
    for i, x in enumerate(cx):
        for r in range(8):
            y = 40 + r * 20
            bit = 0 if zero_rows.get(i) == r else 1
            cls = 'fig-box-claimed' if i == win else 'fig-box'
            out.append(f'<rect x="{x - 14}" y="{y}" width="28" height="18" rx="2" class="{cls}"/>')
            out.append(text(x, y + 13, str(bit), 'fig-label' if bit == 0 else 'fig-muted', 'middle'))
        out.append(f'<rect x="{x - 30}" y="215" width="60" height="30" rx="4" class="{"fig-fill-1" if i == win else "fig-box"}"/>')
        out.append(tex(x, 22, f'X_{i + 1}', f'X_{i + 1}', 'fig-muted', 'middle'))
    for i, x in enumerate(cx):
        if i == win:
            continue
        r = zero_rows[i]
        out.append(arrow(cx[win], 215, x + (16 if x < cx[win] else -16), 40 + r * 20 + 9, 'fig-line-2'))
    out.append(text(cx[win], 264, 'certificate of the winning column', 'fig-label', 'middle'))
    out.append(text(cx[win], 282, 'points to a 0 in every other column', 'fig-muted', 'middle'))
    out.append(text(cx[0], 264, 'address cells', 'fig-muted', 'middle'))
    out.append(text(cx[0], 282, '(set by Forrelation answers)', 'fig-muted', 'middle'))
    return svg(W, H + 10, ''.join(out))


if __name__ == '__main__':
    for name, draw in (('ladder.svg', ladder), ('construction.svg', construction)):
        (HERE / name).write_text(draw())
        print('wrote', name)
