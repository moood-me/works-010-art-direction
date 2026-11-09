"""Placing heads on bodies: each head is drawn in its own 500x600 frame; ANCHOR is its chin."""

ANCHOR = {'anya': (240, 363), 'savely': (236, 428), 'tim': (234, 398), 'vera': (245, 384),
          'marat': (262, 470), 'kira': (246, 372)}


def place(d, out, draw, name, at, s, rot=0, expr='calm'):
    cx, cy = ANCHOR[name]
    out.append(f'<g transform="translate({at[0]},{at[1]}) rotate({rot}) scale({s}) translate({-cx},{-cy})">')
    draw(d, out, expr)
    out.append('</g>')
