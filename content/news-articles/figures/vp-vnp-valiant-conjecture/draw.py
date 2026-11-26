"""Draw the figures for the VP versus VNP article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
Labels carrying data-tex are typeset by MathJax on the page; the plain text is the fallback.
"""
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent


def svg(width, height, body):
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{body}</svg>\n'


def text(x, y, s, cls='fig-text', anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def tex(x, y, plain, latex, cls='fig-label', anchor='start'):
    return text(x, y, plain, cls, anchor, f' data-tex="{escape(latex)}"')


def line(p, q, cls='fig-link'):
    return f'<path d="M{p[0]:.1f},{p[1]:.1f} L{q[0]:.1f},{q[1]:.1f}" class="{cls}"/>'


def circuit():
    """A five-gate circuit whose output has eight terms: (x1+y1)(x2+y2)(x3+y3)."""
    W, H = 640, 390
    out = []
    xs = [(70 + 180 * i, 250) for i in range(3)]
    ys = [(150 + 180 * i, 250) for i in range(3)]
    plus = [(110 + 180 * i, 170) for i in range(3)]
    t1, t2 = (200, 100), (380, 42)
    for i in range(3):
        out += [line(xs[i], plus[i]), line(ys[i], plus[i])]
    out += [line(plus[0], t1), line(plus[1], t1), line(t1, t2), line(plus[2], t2)]
    for i in range(3):
        for (x, y), lab in ((xs[i], f'x{i + 1}'), (ys[i], f'y{i + 1}')):
            out.append(f'<rect x="{x - 20}" y="{y - 14}" width="40" height="28" rx="4" class="fig-box"/>')
            out.append(tex(x, y + 5, lab, f'{lab[0]}_{lab[1]}', 'fig-label', 'middle'))
    for (x, y), op, cls in [(p, '+', 'fig-box') for p in plus] + [(t1, '×', 'fig-box-claimed'), (t2, '×', 'fig-box-claimed')]:
        out.append(f'<circle cx="{x}" cy="{y}" r="18" class="{cls}"/>')
        out.append(text(x, y + 6, op, 'fig-label', 'middle', ' font-size="18"'))
    out.append(tex(320, 304, '(x1+y1)(x2+y2)(x3+y3)', r'(x_1+y_1)(x_2+y_2)(x_3+y_3)', 'fig-text', 'middle'))
    out.append(text(320, 328, '= x1x2x3 + x1x2y3 + … + y1y2y3', 'fig-muted', 'middle',
                    f' data-tex="{escape(r"=x_1x_2x_3+x_1x_2y_3+\dots+y_1y_2y_3")}"'))
    out.append(text(320, 356, '5 gates, 8 terms', 'fig-label', 'middle'))
    out.append(text(320, 378, 'with n pairs: 2n − 1 gates, 2ⁿ terms', 'fig-muted', 'middle',
                    f' data-tex="{escape(r"\text{with } n \text{ pairs: } 2n-1 \text{ gates, } 2^n \text{ terms}")}"'))
    return svg(W, H, ''.join(out))


if __name__ == '__main__':
    (HERE / 'circuit.svg').write_text(circuit())
    print('wrote circuit.svg')
