"""Portraits of Марат and Кира for S6: the same cameo as the four — a profile against a disc of light.
Hand-written paths (facing right); the whole bust is then leaned: he back in a laugh, she forward in her slouch."""
import math, re, sys
import portraits


def lean(d, deg, cx=230, cy=470):
    """Turn every point of a path (absolute M/C/L only) by deg about (cx, cy)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    out, pair = [], []
    for tok in re.findall(r'[MCLZ]|-?\d+\.?\d*', d):
        if tok in 'MCLZ':
            out.append(tok)
        else:
            pair.append(float(tok))
            if len(pair) == 2:
                x, y = pair[0] - cx, pair[1] - cy
                out.append('%.1f %.1f' % (cx + x * c - y * s, cy + x * s + y * c))
                pair = []
    return ' '.join(out)


MARAT_LEAN, KIRA_LEAN = -9, 9

MORE = {
    'marat': dict(
        # curls all round the head, a heavy brow, a broad nose, the moustache over a mouth open in a laugh, a spade of a beard,
        # a short thick neck, shoulders wider than the picture
        d=lean("""M -40 560 C -30 470 30 404 100 384 C 130 376 154 362 162 346
           C 152 340 146 326 153 313 C 144 304 141 287 149 274 C 140 261 141 241 151 230
           C 145 213 150 193 163 186 C 161 168 173 152 189 150 C 194 134 212 126 228 132
           C 240 121 264 121 276 132 C 292 124 311 134 315 149 C 329 155 335 168 330 180
           C 336 190 340 200 342 210 C 348 214 350 222 344 228
           C 350 240 368 262 378 276 C 384 288 374 298 356 296 C 351 296 348 297 346 300
           C 356 300 366 304 366 313 C 366 319 358 321 350 320
           C 338 322 328 325 320 331 C 332 338 344 344 350 352
           C 358 360 364 378 358 394 C 352 410 340 420 326 425
           C 372 436 430 470 470 560 Z""", MARAT_LEAN),
        extra=[],
        bg=('#1c1513', '#6b4333'), disc=(248, 238, 168, '#eccaa4'), rim='#ffc08a', rim2='#d19a7c',
        accent=[('glow', 60, 470, 200, '#ff9c58'),
                # the towel over the shoulder
                ('path', lean("M 196 412 C 214 400 240 402 254 418 C 272 446 284 500 290 560 L 238 560 C 234 508 226 462 210 440 C 204 432 198 424 196 412 Z", MARAT_LEAN), '#f1e3c8')],
        flip=False),
    'kira': dict(
        # a short choppy cut, the fringe hanging past the brow in sharp ends, a small sharp nose, the lips pressed,
        # a pointed chin, a thin neck out of a hood too big for her
        d=lean("""M 60 560 C 66 480 84 432 122 408 C 112 392 120 368 146 362 C 160 358 172 352 180 342
           L 160 348 L 172 326 L 146 330 L 160 306
           C 142 280 134 240 146 204 C 158 166 196 138 240 138 C 278 138 308 156 324 184
           C 336 204 344 236 342 280 L 333 250 L 328 270 L 324 252
           C 330 276 340 288 346 297 C 348 303 342 306 334 306 C 332 310 332 314 334 318
           C 338 322 336 327 330 328 C 334 332 334 337 328 340 C 324 344 324 348 326 354
           C 330 364 324 376 310 378 C 294 380 276 374 262 364
           C 262 380 264 394 270 406 C 300 414 330 440 350 560 Z""", KIRA_LEAN),
        extra=[],
        bg=('#15111d', '#463757'), disc=(236, 250, 158, '#cfc4e2'), rim='#d9c9f2', rim2='#8f7fb4',
        # the headphones round the neck: the near cup under the jaw, the band going round the nape into the hood
        accent=[('line', lean("M 238 372 C 214 364 184 362 150 372", KIRA_LEAN), '#d2ee3c', 9),
                ('path', lean("M 224 366 C 244 360 262 372 264 394 C 266 418 254 436 236 436 C 218 436 208 418 208 396 C 208 382 214 370 224 366 Z", KIRA_LEAN), '#d2ee3c'),
                ('path', lean("M 228 380 C 240 376 250 384 251 398 C 252 412 245 422 236 422 C 226 422 221 412 221 400 C 221 390 223 383 228 380 Z", KIRA_LEAN), '#aac42c')],
        flip=True),
}
portraits.PROFILES.update(MORE)

if __name__ == '__main__':
    for n in (sys.argv[1:] or MORE):
        portraits.portrait(n)
