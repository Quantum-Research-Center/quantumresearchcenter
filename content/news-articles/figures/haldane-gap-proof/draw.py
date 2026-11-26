"""Draw the figures for the Haldane gap article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
Labels carrying data-tex are typeset by MathJax on the page; the plain text is the fallback.
The finite-ring gaps are exact-diagonalization values (S^z sectors, Lanczos) computed for this article.
"""
import math
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Triplet gap E1 - E0 of the periodic spin-1 Heisenberg ring, from exact diagonalization.
GAPS = {4: 1.000000, 6: 0.720627, 8: 0.593555, 10: 0.524808, 12: 0.484196}
BULK = 0.4105      # White and Huse (1993), DMRG
LU = (36, 0.0729)  # Lu (2026): proved for every even L >= 36
OAI = (2304, math.log(20) / 784)  # OpenAI: proved for every even L >= 2304


def svg(width, height, body):
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{body}</svg>\n'


def text(x, y, s, cls='fig-text', anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def tex(x, y, plain, latex, cls='fig-label', anchor='start'):
    return text(x, y, plain, cls, anchor, f' data-tex="{escape(latex)}"')


def path(points, cls, title=None, close=False):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points) + (' Z' if close else '')
    tip = f'<title>{escape(title)}</title>' if title else ''
    return f'<path d="{d}" class="{cls}">{tip}</path>'


def arrow(x1, y1, x2, y2, cls='fig-link', head=9):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.45), y2 - head * math.sin(a - 0.45))
    p2 = (x2 - head * math.cos(a + 0.45), y2 - head * math.sin(a + 0.45))
    return path([(x1, y1), (x2, y2)], cls) + path([p1, (x2, y2), p2], cls)


def spacetime():
    """One partition function, read along imaginary time or along space; and its two doublings."""
    W, H = 640, 300
    out = []

    def torus(x, y, w, h, label_w, label_h, cls='fig-box'):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="{cls}"/>')
        for k in range(1, int(w / 22)):
            out.append(path([(x + k * 22, y), (x + k * 22, y + h)], 'fig-grid'))
        out.append(tex(x + w / 2, y + h + 20, label_w, label_w, 'fig-muted', 'middle'))
        out.append(tex(x - 10, y + h / 2 + 4, label_h, label_h, 'fig-muted', 'end'))

    torus(70, 40, 132, 110, 'n', r'\beta')
    out.append(arrow(214, 140, 214, 50, 'fig-line-2'))
    out.append(tex(222, 70, 'Tr e^{-beta H_n}', r'\operatorname{Tr}e^{-\beta H_n}', 'fig-label'))
    out.append(arrow(80, 30, 192, 30, 'fig-line-1'))
    out.append(tex(136, 20, 'Tr X_beta^n', r'\operatorname{Tr}X_\beta^{\,n}', 'fig-label', 'middle'))
    out.append(text(136, 200, 'one partition function Z_n(beta)', 'fig-text', 'middle',
                    f' data-tex="{escape(r"\text{one partition function } Z_n(\beta)")}"'))

    torus(360, 95, 220, 55, '2n', r'\beta', 'fig-box-claimed')
    out.append(tex(470, 82, 'spatial purity Z_2n(b)/Z_n(b)^2', r'\dfrac{Z_{2n}(\beta)}{Z_n(\beta)^2}', 'fig-label', 'middle'))
    out.append(text(470, 192, 'doubling the ring squares the spatial weights', 'fig-muted', 'middle'))
    torus(360, 205, 110, 66, 'n', r'2\beta', 'fig-box-open')
    out.append(tex(560, 245, 'thermal purity', r'\dfrac{Z_{n}(2\beta)}{Z_n(\beta)^2}', 'fig-label', 'middle'))
    out.append(text(415, 304, 'doubling beta squares the Boltzmann weights', 'fig-muted', 'middle',
                    f' data-tex="{escape(r"\text{doubling } \beta \text{ squares the Boltzmann weights}")}"'))
    return svg(W, H + 20, ''.join(out))


def bootstrap():
    """The staircase: alternate doublings carry both defects from a finite seed to every larger ring."""
    W, H = 640, 330
    x0, y0 = 90, 290
    X = lambda j: x0 + j * 150
    Y = lambda j: y0 - j * 80
    out = [f'<path d="M{x0 - 20},{y0 + 10} H{W - 20} M{x0 - 20},{y0 + 10} V20" class="fig-axis"/>']
    labels = [('n0', 'n_0'), ('2n0', '2n_0'), ('4n0', '4n_0'), ('8n0', '8n_0')]
    for j, (plain, latex) in enumerate(labels):
        out.append(tex(X(j), y0 + 30, plain, latex, 'fig-muted', 'middle'))
    for j, (plain, latex) in enumerate((('b0', r'\beta_0'), ('2b0', r'2\beta_0'), ('4b0', r'4\beta_0'))):
        out.append(tex(x0 - 30, Y(j) + 4, plain, latex, 'fig-muted', 'end'))
    eps = [r'\varepsilon', r'\approx\varepsilon^2', r'\approx\varepsilon^4']
    for j in range(3):
        out.append(path([(X(j), Y(j)), (X(j + 1), Y(j))], 'fig-line-1', 'Interpolation covers every even length in this interval'))
        out.append(f'<circle cx="{X(j):.1f}" cy="{Y(j):.1f}" r="6" class="fig-fill-2"><title>Both purity defects are bounded at this point</title></circle>')
        out.append(tex(X(j) - 10, Y(j) - 12, 'defect', eps[j], 'fig-label', 'end'))
        if j < 2:
            out.append(arrow(X(j) + 8, Y(j) - 6, X(j + 1) - 8, Y(j + 1) + 8, 'fig-ref'))
    out.append(text(X(0) + 70, Y(0) + 22, 'every even length, same beta', 'fig-muted', 'middle',
                    f' data-tex="{escape(r"\text{every even length at } \beta_0")}"'))
    out.append(text(X(0) + 60, Y(0) - 50, 'double n and beta', 'fig-muted', 'end',
                    f' data-tex="{escape(r"\text{double } n \text{ and } \beta")}"'))
    out.append(tex(W - 30, 40, 'gap >= log(1/eps)/beta stays fixed',
                   r'\gamma_L\ \ge\ \tfrac{1}{\beta_j}\log\tfrac{1}{\varepsilon_j}\ \text{ stays fixed}', 'fig-label', 'end'))
    out.append(text(W - 30, y0 + 52, 'ring length', 'fig-muted', 'end'))
    out.append(text(24, 24, 'inverse temperature', 'fig-muted'))
    return svg(W, H + 40, ''.join(out))


def gaps():
    """Finite-ring gaps from exact diagonalization, the numerical bulk value, and the proved lower bounds."""
    W, H = 640, 320
    x0, x1, y0, y1 = 64, 610, 270, 20
    lo, hi = math.log10(3.5), math.log10(10000)
    X = lambda L: x0 + (math.log10(L) - lo) / (hi - lo) * (x1 - x0)
    Y = lambda g: y0 - g / 1.05 * (y0 - y1)
    out = []
    for g in (0, 0.25, 0.5, 0.75, 1.0):
        out.append(f'<path d="M{x0},{Y(g):.1f} H{x1}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(g) + 4, f'{g:g}', 'fig-muted', 'end'))
    for L in (4, 10, 100, 1000, 10000):
        out.append(text(X(L), y0 + 18, f'{L:,}', 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    out.append(path([(X(4), Y(BULK)), (X(10000), Y(BULK))], 'fig-ref', 'DMRG estimate of the bulk gap, 0.4105'))
    out.append(text(X(10000) - 4, Y(BULK) - 8, 'numerical bulk gap 0.4105 (White–Huse)', 'fig-muted', 'end'))
    pts = [(X(L), Y(g)) for L, g in GAPS.items()]
    out.append(path(pts, 'fig-line-1'))
    for (L, g), (x, y) in zip(GAPS.items(), pts):
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="fig-fill-1"><title>L = {L}: gap {g:.4f}</title></circle>')
    out.append(tex(X(12) + 10, Y(GAPS[12]) - 10, 'exact gaps, L = 4 to 12', r'\text{exact gaps, } L=4 \text{ to } 12', 'fig-text'))
    out.append(path([(X(LU[0]), Y(LU[1])), (X(10000), Y(LU[1]))], 'fig-line-2', 'Proved by Lu: gap above 0.0729 for every even L >= 36'))
    out.append(path([(X(60), Y(0.19)), (X(60), Y(LU[1]))], 'fig-link'))
    out.append(tex(X(60) - 6, Y(0.21), 'proved: > 0.0729 for L >= 36 (Lu)', r'\text{proved: } \gamma_L>0.0729 \text{ for } L\ge36 \text{ (Lu)}', 'fig-label', 'start'))
    out.append(path([(X(OAI[0]), Y(OAI[1])), (X(10000), Y(OAI[1]))], 'fig-line-2', 'Proved by OpenAI: gap above 0.0038 for every even L >= 2304'))
    out.append(path([(X(5000), Y(0.10)), (X(5000), Y(OAI[1]))], 'fig-link'))
    out.append(tex(X(10000) - 4, Y(0.12), 'proved: > 0.0038 for L >= 2304 (OpenAI)', r'\text{proved: } \gamma_L>0.0038 \text{ for } L\ge2304 \text{ (OpenAI)}', 'fig-label', 'end'))
    out.append(text((x0 + x1) / 2, H - 6, 'ring length L (log scale)', 'fig-muted', 'middle',
                    f' data-tex="{escape(r"\text{ring length } L \text{ (log scale)}")}"'))
    out.append(tex(18, (y0 + y1) / 2, 'gap', r'\gamma_L', 'fig-label', 'middle'))
    return svg(W, H, ''.join(out))


if __name__ == '__main__':
    for name, draw in (('spacetime.svg', spacetime), ('bootstrap.svg', bootstrap), ('gaps.svg', gaps)):
        (HERE / name).write_text(draw())
        print('wrote', name)
