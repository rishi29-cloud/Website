#!/usr/bin/env python3
"""Generate the hero's expected-range chart and inject it into index.html.

The hero is the one bold element on the page: a metric trace inside the
shaded confidence band that observability tools draw around an expected
value, with a single excursion that breaks the upper bound. The geometry is
deterministic (fixed seed), so re-running this reproduces the same curve.

Run from the project root:  python3 build_hero.py
"""

import math
import random
from pathlib import Path

W, H = 1200, 460          # viewBox; the SVG stretches to fit, strokes do not
SAMPLES = 92              # points in the trace
BREACH = 79               # index of the excursion
SEED = 11

ROOT = Path(__file__).resolve().parent
START = "<!--hero-visual:start-->"
END = "<!--hero-visual:end-->"


def centre(x):
    """Expected value: a slow seasonal drift."""
    t = x / W
    return 230 + 16 * math.sin(t * 3.1 + 0.6) - 10 * math.sin(t * 1.3)


def half_width(x):
    """Half the expected range, widening as the forecast horizon grows."""
    t = x / W
    return 44 + 28 * t + 7 * math.sin(t * 5.2)


def smooth(points, places=0):
    """Catmull-Rom through the points, emitted as cubic beziers."""
    fmt = "{:." + str(places) + "f}"
    out = ["M" + fmt.format(points[0][0]) + " " + fmt.format(points[0][1])]
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[0]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(
            "C"
            + " ".join(fmt.format(v) for v in (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
        )
    return " ".join(out)


def build():
    # --- the band: few samples, since the bounds are analytic curves ---
    band_xs = [i * W / 18 for i in range(19)]
    upper = [(x, centre(x) - half_width(x)) for x in band_xs]
    lower = [(x, centre(x) + half_width(x)) for x in band_xs]

    upper_d = smooth(upper)
    lower_d = smooth(lower)
    band_d = upper_d + " L" + lower_d[1:].strip() + " Z"

    # --- the trace: a mean-reverting walk that mostly stays in range ---
    random.seed(SEED)
    xs = [i * W / (SAMPLES - 1) for i in range(SAMPLES)]
    walk, v = [], 0.0
    for _ in xs:
        v += random.gauss(0, 0.32)
        v *= 0.85                       # pull back toward the expected value
        walk.append(v)

    peak = max(abs(min(walk)), abs(max(walk)))
    walk = [v / peak * 0.70 for v in walk]   # keep inside the band

    for index, factor in ((BREACH - 1, 1.03), (BREACH, 1.66),
                          (BREACH + 1, 1.18), (BREACH + 2, 0.52)):
        walk[index] = factor                 # the excursion

    points = [(x, centre(x) - walk[i] * half_width(x)) for i, x in enumerate(xs)]
    trace_d = smooth(points)

    bx, by = points[BREACH]
    left, top = bx / W * 100, by / H * 100

    return f"""{START}
            <div class="hero-trace" aria-hidden="true">
              <svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" focusable="false">
                <path class="trace-band" d="{band_d}" />
                <path class="trace-bound" d="{upper_d}" />
                <path class="trace-bound" d="{lower_d}" />
                <path class="trace-line" d="{trace_d}" />
              </svg>
              <span class="trace-point" style="left:{left:.2f}%;top:{top:.2f}%"></span>
              <span class="trace-label is-breach" style="left:{left:.2f}%;top:{top:.2f}%">anomaly</span>
              <span class="trace-label is-range">expected range</span>
              <span class="trace-label is-note">illustrative, not live data</span>
            </div>
            {END}"""


def main():
    page = ROOT / "index.html"
    html = page.read_text(encoding="utf-8")

    start, end = html.find(START), html.find(END)
    if start == -1 or end == -1:
        raise SystemExit("hero-visual markers not found in index.html")

    html = html[:start] + build() + html[end + len(END):]
    page.write_text(html, encoding="utf-8")
    print("injected hero chart into", page.name)


if __name__ == "__main__":
    main()
