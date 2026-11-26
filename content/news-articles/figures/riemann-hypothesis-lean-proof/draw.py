"""Draw the figures for the Riemann hypothesis article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
Labels carrying data-tex are typeset by MathJax on the page; the plain text is the fallback.
The zero ordinates below are the first 100 zeros of zeta (mpmath.zetazero, rounded to 6 places).
"""
import math
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

ZEROS = [14.134725, 21.02204, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073, 48.005151,
         49.773832, 52.970321, 56.446248, 59.347044, 60.831779, 65.112544, 67.079811, 69.546402, 72.067158,
         75.704691, 77.14484, 79.337375, 82.910381, 84.735493, 87.425275, 88.809111, 92.491899, 94.651344,
         95.870634, 98.831194, 101.317851, 103.725538, 105.446623, 107.168611, 111.029536, 111.874659,
         114.320221, 116.22668, 118.790783, 121.370125, 122.946829, 124.256819, 127.516684, 129.578704,
         131.087689, 133.497737, 134.75651, 138.116042, 139.736209, 141.123707, 143.111846, 146.000982,
         147.422765, 150.05352, 150.925258, 153.024694, 156.112909, 157.597592, 158.849988, 161.188964,
         163.03071, 165.537069, 167.18444, 169.094515, 169.911976, 173.411537, 174.754192, 176.441434,
         178.377408, 179.916484, 182.207078, 184.874468, 185.598784, 187.228923, 189.416159, 192.026656,
         193.079727, 195.265397, 196.876482, 198.01531, 201.264752, 202.493595, 204.189672, 205.394697,
         207.906259, 209.57651, 211.690863, 213.347919, 214.547045, 216.169539, 219.067596, 220.714919,
         221.430706, 224.007, 224.983325, 227.421444, 229.337413, 231.250189, 231.987235, 233.693404, 236.52423]


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


def strip():
    """The complex s-plane: where the series converges, the pole, trivial zeros, and the first zeros on the line."""
    W, H = 640, 400
    x0, x1, ym = 40, 620, 200
    X = lambda re: x0 + (re + 8) / 11.5 * (x1 - x0)      # Re s from -8 to 3.5
    Y = lambda im: ym - im * 4.9                          # Im s from about -37 to 37
    out = [f'<rect x="{X(0):.1f}" y="14" width="{X(1) - X(0):.1f}" height="{H - 50}" class="fig-wash-1"><title>Critical strip, 0 &lt; Re s &lt; 1</title></rect>',
           f'<rect x="{X(1):.1f}" y="14" width="{x1 - X(1):.1f}" height="{H - 50}" class="fig-fill-muted-soft"><title>Re s &gt; 1: the series for zeta converges</title></rect>',
           f'<path d="M{x0},{ym} H{x1}" class="fig-axis"/>', f'<path d="M{X(0):.1f},14 V{H - 36}" class="fig-axis"/>',
           f'<path d="M{X(0.5):.1f},14 V{H - 36}" class="fig-measure"/>']
    for re in range(-8, 4, 2):
        out.append(f'<path d="M{X(re):.1f},{ym - 4} V{ym + 4}" class="fig-axis"/>')
        if re not in (0,):
            out.append(text(X(re), ym + 18, str(re).replace('-', '−'), 'fig-muted', 'middle'))
    for t in ZEROS[:4]:
        for sign in (1, -1):
            out.append(f'<circle cx="{X(0.5):.1f}" cy="{Y(sign * t):.1f}" r="5" class="fig-fill-1"><title>Zero at 1/2 {"+" if sign > 0 else "−"} {t:.3f} i</title></circle>')
    out.append(text(X(0.5) + 10, Y(ZEROS[0]) + 4, '14.13…', 'fig-muted'))
    for re in (-2, -4, -6):
        out.append(f'<circle cx="{X(re):.1f}" cy="{ym}" r="5" class="fig-hollow"><title>Trivial zero at s = {re}</title></circle>')
    px = X(1)
    out.append(f'<path d="M{px - 6:.1f},{ym - 6} L{px + 6:.1f},{ym + 6} M{px - 6:.1f},{ym + 6} L{px + 6:.1f},{ym - 6}" class="fig-cross"><title>Pole at s = 1</title></path>')
    out.append(tex(X(-4), ym - 16, 'trivial zeros −2, −4, −6, …', r'\text{trivial zeros }{-2},{-4},{-6},\dots', 'fig-text', 'middle'))
    out.append(tex(X(0.5) - 10, 30, 'Re s = 1/2', r'\operatorname{Re}s=\tfrac12', 'fig-label', 'end'))
    out.append(tex(X(1) + 12, ym - 12, 'pole at s = 1', r'\text{pole at } s=1', 'fig-text'))
    out.append(tex(X(1) + 12, 40, 'sum of n^−s converges', r'\textstyle\sum n^{-s}\text{ converges}', 'fig-text'))
    out.append(text((X(0) + X(1)) / 2, H - 16, 'critical strip', 'fig-muted', 'middle'))
    out.append(text(x1, ym + 18, 'Re s', 'fig-muted', 'end'))
    return svg(W, H, ''.join(out))


def primes(n):
    return [p for p in range(2, n + 1) if all(p % q for q in range(2, int(p ** 0.5) + 1))]


def psi(x):
    """Chebyshev's function: log p summed over prime powers p^k up to x."""
    return sum(math.log(p) for p in primes(int(x)) for k in range(1, 40) if p ** k <= x)


def explicit(x, n):
    """Riemann–von Mangoldt explicit formula truncated to the first n conjugate pairs of zeros (assumed on the line)."""
    r = x - math.log(2 * math.pi) - 0.5 * math.log(1 - x ** -2)
    for t in ZEROS[:n]:
        rho = complex(0.5, t)
        r -= 2 * (x ** rho / rho).real
    return r


def staircase():
    """psi(x) and the explicit formula with 3 and 100 pairs of zeros."""
    W, H = 640, 340
    x0, x1, y0, y1 = 56, 620, 290, 20
    lo, hi, top = 1.5, 40, 40
    X = lambda x: x0 + (x - lo) / (hi - lo) * (x1 - x0)
    Y = lambda v: y0 - v / top * (y0 - y1)
    out = []
    for v in range(0, top + 1, 10):
        out.append(f'<path d="M{x0},{Y(v):.1f} H{x1}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(v) + 4, str(v), 'fig-muted', 'end'))
    for x in (10, 20, 30, 40):
        out.append(text(X(x), y0 + 18, str(x), 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    out.append(path([(X(lo), Y(lo)), (X(hi), Y(hi))], 'fig-ref', 'The main term x'))
    steps, prev = [], 0.0
    for k in range(2, hi + 1):
        v = psi(k)
        if v != prev:
            steps += [(X(k), Y(prev)), (X(k), Y(v))]
            prev = v
    out.append(path([(X(lo), Y(0))] + steps + [(X(hi), Y(prev))], 'fig-link', 'Chebyshev psi(x): jumps by log p at each prime power'))
    xs = [lo + i * (hi - lo) / 900 for i in range(901)]
    out.append(path([(X(x), Y(explicit(x, 3))) for x in xs], 'fig-line-2', 'Explicit formula with 3 pairs of zeros'))
    out.append(path([(X(x), Y(explicit(x, 100))) for x in xs], 'fig-line-1', 'Explicit formula with 100 pairs of zeros'))
    lx = x0 + 14
    for i, (cls, plain, latex) in enumerate((('fig-link', 'ψ(x)', r'\psi(x)'),
                                              ('fig-ref', 'x', r'x'),
                                              ('fig-line-2', '3 zeros', r'\text{3 pairs of zeros}'),
                                              ('fig-line-1', '100 zeros', r'\text{100 pairs of zeros}'))):
        y = y1 + 12 + i * 20
        out.append(f'<path d="M{lx},{y} h26" class="{cls}"/>')
        out.append(tex(lx + 34, y + 4, plain, latex, 'fig-text'))
    out.append(text((x0 + x1) / 2, H - 6, 'x', 'fig-muted', 'middle'))
    return svg(W, H, ''.join(out))


if __name__ == '__main__':
    for name, draw in (('strip.svg', strip), ('staircase.svg', staircase)):
        (HERE / name).write_text(draw())
        print('wrote', name)
