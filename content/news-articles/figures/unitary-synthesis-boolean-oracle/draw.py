"""Draw the figures for the unitary synthesis article. Run: python3 draw.py (writes the .svg files beside it).

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


def path(points, cls, close=False):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points) + (' Z' if close else '')
    return f'<path d="{d}" class="{cls}"/>'


def arrow(x1, y1, x2, y2, cls='fig-link', head=8):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.45), y2 - head * math.sin(a - 0.45))
    p2 = (x2 - head * math.cos(a + 0.45), y2 - head * math.sin(a + 0.45))
    return path([(x1, y1), (x2, y2)], cls) + path([p1, (x2, y2), p2], cls)


def model():
    """One circuit for each n, fixed gates and oracle calls; only the Boolean oracle depends on U."""
    W, H = 640, 270
    out = []
    wires = [40, 62, 84, 120, 142, 164, 186]
    for y in wires:
        out.append(path([(120, y), (580, y)], 'fig-link'))
    out.append(tex(110, 66, 'n input qubits', r'n\ \text{qubits}', 'fig-muted', 'end'))
    out.append(text(110, 158, 'workspace', 'fig-muted', 'end'))
    out.append(text(110, 174, 'starting at 0', 'fig-muted', 'end'))
    xs = [150, 210, 270, 330, 390, 450, 510]
    for i, x in enumerate(xs):
        if i % 2 == 1:
            out.append(f'<rect x="{x - 22}" y="{110}" width="44" height="86" rx="4" class="fig-box-claimed"/>')
            out.append(tex(x, 158, 'O_f', r'O_f', 'fig-label', 'middle'))
        else:
            out.append(f'<rect x="{x - 20}" y="{30}" width="40" height="166" rx="4" class="fig-box"/>')
            out.append(text(x, 118, 'gates', 'fig-muted', 'middle'))
    out.append(tex(590, 66, 'approximately U', r'\approx U', 'fig-label'))
    out.append(text(350, 222, 'the same circuit for every n-qubit unitary', 'fig-text', 'middle',
                    f' data-tex="{escape(r"\text{the same circuit for every } n\text{-qubit unitary}")}"'))
    out.append(f'<rect x="200" y="236" width="300" height="28" rx="4" class="fig-box-open"/>')
    out.append(tex(350, 255, 'f: {0,1}^m -> {0,1}, chosen for U', r'f:\{0,1\}^m\to\{0,1\}\ \text{chosen for } U', 'fig-label', 'middle'))
    return svg(W, H + 10, ''.join(out))


def feedback():
    """Closing the contracting block of a unitary through a diagonal phase leaves a smaller unitary."""
    W, H = 640, 290
    out = []
    bx, by, bw, bh = 220, 40, 200, 160
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" class="fig-box"/>')
    out.append(path([(bx, by + bh * 0.55), (bx + bw, by + bh * 0.55)], 'fig-grid'))
    out.append(path([(bx + bw * 0.55, by), (bx + bw * 0.55, by + bh)], 'fig-grid'))
    for (px, py, plain, latex) in ((bx + bw * 0.27, by + bh * 0.3, 'A', 'A'), (bx + bw * 0.78, by + bh * 0.3, 'B', 'B'),
                                   (bx + bw * 0.27, by + bh * 0.8, 'C', 'C'), (bx + bw * 0.78, by + bh * 0.8, 'D', 'D')):
        out.append(tex(px, py + 6, plain, latex, 'fig-label', 'middle'))
    yk, ys = by + bh * 0.3, by + bh * 0.8
    out.append(arrow(80, yk, bx, yk, 'fig-line-1'))
    out.append(arrow(bx + bw, yk, 560, yk, 'fig-line-1'))
    out.append(tex(70, yk + 5, 'kept', r'\text{kept } (k)', 'fig-muted', 'end'))
    out.append(tex(570, yk + 5, 'out', r'F\,x', 'fig-label'))
    # feedback loop on the removed coordinates
    lx = bx + bw + 40
    out.append(path([(bx + bw, ys), (lx, ys), (lx, 250), (bx - 40, 250), (bx - 40, ys)], 'fig-line-2'))
    out.append(arrow(bx - 40, ys, bx, ys, 'fig-line-2'))
    out.append(f'<rect x="{(bx + lx) / 2 - 60}" y="232" width="80" height="36" rx="4" class="fig-box-claimed"/>')
    out.append(tex((bx + lx) / 2 - 20, 256, 'Z', r'Z', 'fig-label', 'middle'))
    out.append(text((bx + lx) / 2 - 20, 284, 'diagonal phases', 'fig-muted', 'middle'))
    out.append(tex(bx - 50, ys + 5, 'removed', r'\text{removed } (s)', 'fig-muted', 'end'))
    out.append(tex(320, 22, 'V = [[A, B], [C, D]], ||D|| <= 3/4', r'V=\begin{pmatrix}A&B\\C&D\end{pmatrix},\quad \|D\|\le\tfrac34', 'fig-label', 'middle'))
    return svg(W, H + 6, ''.join(out))


if __name__ == '__main__':
    for name, draw in (('model.svg', model), ('feedback.svg', feedback)):
        (HERE / name).write_text(draw())
        print('wrote', name)
