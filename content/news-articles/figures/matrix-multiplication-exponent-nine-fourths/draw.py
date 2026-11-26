"""Draw the figures for the matrix multiplication exponent article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
Labels carrying data-tex are typeset by MathJax on the page; the plain text is the fallback.
"""
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Best published upper bounds on omega (year, bound). Values before 2026 from the standard literature;
# 2026 values from OpenAI's September and October preprints.
UPPER = [(1969, 2.8074), (1978, 2.796), (1979, 2.780), (1981, 2.522), (1982, 2.496), (1986, 2.479),
         (1990, 2.3755), (2010, 2.3737), (2012, 2.3729), (2014, 2.37286), (2022, 2.37188), (2023, 2.37155),
         (2024, 2.37134), (2026.73, 2.258), (2026.75, 2.25)]


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


def history():
    """Step chart of the best upper bound on omega, with the trivial lower bound and the claimed exact value."""
    W, H = 640, 330
    x0, x1, y0, y1 = 56, 600, 280, 20
    X = lambda yr: x0 + (yr - 1965) / (2030 - 1965) * (x1 - x0)
    Y = lambda w: y0 - (w - 1.9) / (3.05 - 1.9) * (y0 - y1)
    out = []
    for w in (2.0, 2.25, 2.5, 2.75, 3.0):
        out.append(f'<path d="M{x0},{Y(w):.1f} H{x1}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(w) + 4, f'{w:g}', 'fig-muted', 'end'))
    for yr in (1970, 1980, 1990, 2000, 2010, 2020, 2030):
        out.append(text(X(yr), y0 + 18, str(yr), 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    pts, prev = [(X(1965), Y(3.0)), (X(1969), Y(3.0))], 3.0
    for yr, w in UPPER:
        pts += [(X(yr), Y(prev)), (X(yr), Y(w))]
        prev = w
    pts.append((X(2030), Y(prev)))
    out.append(path(pts, 'fig-line-1', 'Best proved upper bound on omega'))
    for yr, w in UPPER:
        out.append(f'<circle cx="{X(yr):.1f}" cy="{Y(w):.1f}" r="3" class="fig-fill-1"><title>{yr:.0f}: omega &lt; {w}</title></circle>')
    out.append(path([(X(1965), Y(2.0)), (X(2026.9), Y(2.0))], 'fig-line-2', 'Lower bound: omega is at least 2'))
    out.append(path([(X(2026.9), Y(2.0)), (X(2026.9), Y(2.25))], 'fig-ref', 'Claimed lower bound, 24 November 2026'))
    out.append(text(X(1971), Y(2.807) - 8, 'Strassen 1969: 2.807', 'fig-text'))
    out.append(text(X(1991), Y(2.3755) - 30, 'Coppersmith–Winograd 1990: 2.376', 'fig-text'))
    out.append(text(X(2024) - 4, Y(2.3713) + 20, '2024: 2.371', 'fig-text', 'end'))
    out.append(text(X(2026.75) - 8, Y(2.25) + 18, 'OpenAI, Oct 2026: 9/4', 'fig-label', 'end'))
    out.append(tex(X(1972), Y(2.0) - 8, 'trivial lower bound: the n^2 outputs must be written', r'\text{trivial lower bound: the } n^2 \text{ outputs must be written}', 'fig-muted'))
    out.append(text(X(2026.9) - 8, Y(2.12), 'claimed', 'fig-muted', 'end'))
    out.append(text(X(2026.9) - 8, Y(2.12) + 14, 'Nov 2026', 'fig-muted', 'end'))
    out.append(tex(16, (y0 + y1) / 2, 'omega', r'\omega', 'fig-label', 'middle'))
    return svg(W, H, ''.join(out))


def wires():
    """Two descriptions of the matrix multiplication tensor: three wires, or one shared label."""
    W, H = 640, 270
    out = []

    def site(x, y, name):
        out.append(f'<circle cx="{x}" cy="{y}" r="19" class="fig-node"/>')
        out.append(text(x, y + 5, name, 'fig-label', 'middle'))

    A, B, C = (90, 200), (250, 200), (170, 62)
    for (p, q, lab, dx, dy) in ((A, B, 'j', 0, 22), (B, C, 'k', 18, 0), (C, A, 'i', -18, 0)):
        out.append(path([p, q], 'fig-line-1'))
        mx, my = (p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy
        out.append(tex(mx, my + 4, lab, lab, 'fig-label', 'middle'))
    for p, n in ((A, 'A'), (B, 'B'), (C, 'C')):
        site(*p, n)
    out.append(text(170, 246, 'three wires, n values each', 'fig-muted', 'middle'))

    hub = (470, 150)
    A2, B2, C2 = (390, 200), (550, 200), (470, 62)
    for p in (A2, B2, C2):
        out.append(path([hub, p], 'fig-line-2'))
    out.append(f'<circle cx="{hub[0]}" cy="{hub[1]}" r="7" class="fig-fill-2"><title>One label shared by all three factors</title></circle>')
    out.append(tex(hub[0] + 14, hub[1] - 2, 'l', r'\ell', 'fig-label'))
    for p, n in ((A2, 'A'), (B2, 'B'), (C2, 'C')):
        site(*p, n)
    out.append(text(470, 246, 'one shared label, r values', 'fig-muted', 'middle'))
    out.append(text(320, 140, '≤', 'fig-label', 'middle', ' font-size="22"'))
    return svg(W, H, ''.join(out))


if __name__ == '__main__':
    for name, draw in (('history.svg', history), ('wires.svg', wires)):
        (HERE / name).write_text(draw())
        print('wrote', name)
