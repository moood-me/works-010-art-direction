"""Portraits for S6: a profile against a disc of light — the face is its edge. Hand-written paths (facing right)."""
import os, sys
from scenes import save, sky, glow_svg, finish, INK
from draw import uid

PROFILES = {
    'anya': dict(
        d="""M 92 500 C 98 430 108 362 114 302 C 118 244 118 192 140 152 C 162 108 205 84 245 88
           C 280 92 304 116 312 150 C 316 168 318 186 320 200 C 322 206 320 212 314 220
           C 322 236 336 254 346 266 C 352 273 348 280 338 281 C 333 282 329 283 327 287
           C 329 292 334 294 334 299 C 334 303 328 305 327 307 C 331 311 332 316 326 321
           C 324 325 322 327 324 331 C 330 338 330 348 320 354 C 306 360 292 360 280 362
           C 276 380 278 400 286 420 C 302 440 342 458 368 500 Z""",
        # eyelashes: the one detail of the face, past the edge of the profile
        extra=["M 314 217 C 321 216 327 212 331 206 C 329 214 323 221 315 223 Z"],
        bg=('#151b2c', '#3c4565'), disc=(250, 205, 150, '#d9d6e4'), rim='#ffd3a0', rim2='#9fb0d6',
        accent=[('glow', 360, 470, 200, '#ffc47a')], flip=False),
    'savely': dict(
        d="""M 30 500 C 40 410 76 344 140 304 C 160 291 170 282 172 270 C 160 252 158 222 168 202
           C 180 172 220 158 270 158 C 300 158 322 164 336 174 C 356 180 378 186 390 192
           C 393 196 389 199 378 199 C 358 199 340 199 330 204 C 328 214 334 222 338 228
           C 340 234 334 238 330 240 C 340 256 356 272 366 288 C 374 300 366 312 352 308
           C 346 308 342 310 344 314 C 356 318 358 330 346 334 C 350 340 346 344 336 344
           C 336 352 332 360 322 362 C 308 366 298 366 290 372 C 290 384 296 394 302 402
           C 318 410 334 414 346 424 C 362 444 376 468 392 500 Z""",
        extra=["M 320 171 L 346 161 C 351 159 354 169 349 172 L 324 181 Z"],
        bg=('#1d1520', '#5e3c40'), disc=(235, 250, 165, '#e6c9a8'), rim='#ffc27e', rim2='#c79a8a',
        accent=[('glow', 380, 470, 190, '#ffb85a'), ('dot', 348, 165, 3.2, '#ffe2b0')], flip=True),
    'tim': dict(
        d="""M 118 500 C 128 448 150 414 170 397 C 158 382 140 362 132 332 C 120 292 125 242 150 202
           C 175 166 220 146 262 150 C 300 155 322 180 328 212 C 330 226 330 234 326 242
           C 332 252 342 262 350 268 C 356 274 350 282 340 280 C 336 284 336 288 338 292
           C 346 296 344 304 336 304 C 340 310 336 316 330 316 C 334 324 330 334 318 336
           C 306 340 296 340 290 340 C 288 356 292 368 296 374 C 316 396 346 424 362 500 Z""",
        extra=["M 250 150 C 286 144 318 158 334 186 C 322 180 310 179 300 183 C 306 172 288 162 252 162 Z", "M 206 158 C 198 140 204 122 222 112 C 214 126 214 140 222 154 Z", "M 222 154 C 222 138 232 128 246 124 C 238 134 236 144 240 152 Z"],
        bg=('#1a2132', '#6a7592'), disc=(240, 240, 150, '#eef1f7'), rim='#ffe0c4', rim2='#c8d2e8',
        accent=[('scarf', None)], flip=False),
    'vera': dict(
        d="""M 140 500 C 145 452 150 420 160 400 C 175 380 186 360 190 335 C 192 318 186 300 180 288
           C 170 270 166 250 168 232 C 172 180 210 140 258 140 C 294 141 316 162 322 196
           C 324 208 324 214 320 222 C 328 238 342 258 352 276 C 355 282 350 286 342 285
           C 336 286 333 288 334 293 C 336 298 334 302 332 304 C 334 308 333 311 330 313
           C 334 322 336 332 328 340 C 316 346 300 346 292 350 C 290 358 292 364 296 370
           C 306 376 318 386 324 400 C 340 432 360 458 374 500 Z""",
        extra=["M 165 180 m -34 0 a 34 32 0 1 0 68 0 a 34 32 0 1 0 -68 0"],
        bg=('#2a3350', '#b49a95'), disc=(245, 225, 160, '#f3e2d2'), rim='#fff0de', rim2='#d8c0c0',
        accent=[('glasses',)], flip=True),
}


def crescent(d, col, dx, dy, op=1.0, extra=''):
    mid = uid('m')
    return ('<mask id="%s" maskUnits="userSpaceOnUse"><g fill="#fff">%s</g><g fill="#000" transform="translate(%.1f %.1f)">%s</g></mask>'
            '<g fill="%s" opacity="%.2f" mask="url(#%s)">%s</g>') % (mid, d, dx, dy, d, col, op, mid, d)


def portrait(name, W=420, H=500):
    p = PROFILES[name]
    paths = '<path d="%s"/>' % p['d'] + ''.join('<path d="%s"/>' % e for e in p['extra'])
    b = ('<defs><linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/>'
         '<stop offset="1" stop-color="%s"/></linearGradient></defs><rect width="%d" height="%d" fill="url(#pbg)"/>') % (
        p['bg'][0], p['bg'][1], W, H)
    cx, cy, r, col = p['disc']
    g = ''
    g += glow_svg(cx, cy, r * 1.6, col, .7)
    g += '<circle cx="%d" cy="%d" r="%d" fill="%s" opacity=".92"/>' % (cx, cy, r, col)
    back = ''
    front = ''
    for a in p['accent']:
        if a[0] == 'glow':
            g += glow_svg(a[1], a[2], a[3], a[4], 1.0)
        if a[0] == 'dot':
            front += glow_svg(a[1], a[2], a[3] * 7, a[4], .9) + '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % a[1:]
        if a[0] == 'scarf':
            # the red scarf: a band round the neck, a knot, one end flying back
            front += ('<path d="M 280 352 C 300 362 316 372 322 392 C 308 404 284 404 262 396 C 236 388 200 384 168 392 '
                      'C 150 396 128 404 104 398 C 120 392 134 380 150 372 C 186 360 230 352 280 352 Z" fill="#d9472f"/>')
            front += '<path d="M 300 384 C 312 400 318 424 314 448 C 304 440 296 420 292 398 Z" fill="#c23d28"/>'
        if a[0] == 'glasses':
            front += '<path d="M 328 232 L 262 236" stroke="#4a5266" stroke-width="2" fill="none"/>'
            front += '<path d="M 330 224 C 340 224 344 242 340 250 C 336 254 330 252 329 244 Z" fill="#eaf1ff" opacity=".85"/>'
            front += glow_svg(336, 238, 40, '#f4f8ff', .5)
        if a[0] == 'path':      # any flat sign: ('path', d, colour)
            front += '<path d="%s" fill="%s"/>' % a[1:3]
        if a[0] == 'line':      # a thin sign: ('line', d, colour, width)
            front += '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % a[1:4]
    fig = '<g fill="%s">%s</g>' % (INK, paths)
    fig += crescent(paths, p['rim'], -2.6, .6)
    fig += crescent(paths, p['rim2'], 1.6, -.4, .55)
    body = g + back + fig + front
    if p['flip']:
        body = '<g transform="translate(%d 0) scale(-1 1)">%s</g>' % (W, body)
    b += body + finish(W, H, .5)
    save('portrait-' + name, W, H, b)


if __name__ == '__main__':
    for n in (sys.argv[1:] or PROFILES):
        portrait(n)
