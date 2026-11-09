"""The palette of С16: hue-shifted ramps, dark -> light (shadows lean to plum/blue, lights to yellow).
A colour key is a ramp letter and a step: 's3' = skin, step 3. Step 0 of a ramp is its outline colour."""

RAMPS = {
    # skin
    's': ['#6b3348', '#b5655c', '#e29a7c', '#f7cba4', '#fee9cb'],   # fair
    'm': ['#522a3a', '#96503f', '#c98056', '#e9ae7e', '#f8d5a8'],   # tan (Марат)
    # hair
    'a': ['#47192d', '#8c2f2b', '#c4552b', '#ea8c3c', '#f9c466'],   # auburn (Аня)
    'w': ['#4f5676', '#8a93ad', '#c3cad8', '#eef0ec', '#ffffff'],   # white hair, white cloth (cool)
    't': ['#6a3528', '#a8652e', '#dca03c', '#f6d465', '#fdf0a8'],   # sandy (Тим), yellow cloth (Аня)
    'v': ['#17142b', '#2a2748', '#45446e', '#6f74a0', '#a3acd0'],   # blue-black (Вера), navy cloth
    'b': ['#1d1420', '#3a2329', '#5e3b33', '#8a5c41', '#b98a5c'],   # brown-black (Марат), leather, wood
    'p': ['#150f1c', '#291a33', '#46294f', '#6f4578', '#9a6da0'],   # plum (Кира)
    # cloth
    'e': ['#12303f', '#1c5560', '#2c8779', '#63bf97', '#b4e6b4'],   # teal
    'g': ['#1b3230', '#31523a', '#587d43', '#93ad57', '#cfd98a'],   # moss green
    'r': ['#5c1a33', '#a52b3b', '#dc4f40', '#f5875c', '#fcbd8c'],   # red
    'u': ['#1b2148', '#2c4688', '#4777c0', '#7bb2e6', '#bfe0f6'],   # blue
    'c': ['#7a5a5e', '#c2a595', '#ecdcc2', '#fff8e6', '#ffffff'],   # warm white (Марат)
    'o': ['#5e2330', '#a2402d', '#d8662d', '#f29848', '#fbc878'],   # terracotta
    'n': ['#121219', '#23232d', '#393a46', '#585a68', '#838694'],  # charcoal
    'l': ['#4c6a1c', '#8fb01e', '#cde530', '#f1fb80', '#fbffc8'],   # acid lime (Кира's accent)
    'x': ['#1f1629', '#ffffff', '#f08a84', '#d0607a', '#fff6d8'],   # x0 ink, x1 white, x2 blush, x3 lip, x4 glint
    'z': ['#f4b09a', '#dd8f6c', '#ee9d8a', '#f4b09a', '#f4b09a'],   # blush laid on skin: z0 fair, z1 tan, z2 an old nose
    # scenery
    'd': ['#231c38', '#3a2f55', '#5a4a72', '#8a6f8c', '#c9a0a0'],   # dusk stone
    'k': ['#2b2440', '#4b3a5e', '#8a4f6a', '#d9795c', '#f6b36a'],   # dusk sky
    'h': ['#f6b84a', '#fbd97a', '#fff2b8', '#ffffff', '#ffffff'],   # lamp light
}


def hexof(key):
    return RAMPS[key[0]][int(key[1])]


def darker(key, n=1):
    return key[0] + str(max(0, int(key[1]) - n))


def lighter(key, n=1):
    return key[0] + str(min(len(RAMPS[key[0]]) - 1, int(key[1]) + n))
