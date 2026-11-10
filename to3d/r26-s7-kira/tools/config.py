"""Who this folder builds (the same tools serve Вера Р25 and Кира Р26; only this file differs)."""
WHO = 'kira'                               # the character's module in styles/s7-ghibli/tools
FOLDER = 'r26-s7-kira'
CACHE = '/home/user/cache/to3d-r26-s7-kira'
LABEL = 'Кира, Гибли'
BODY = 'moood-woman'                       # the engine body whose hands, skeleton and weights are used
CALM = None                                # her resting face is in her own module (kira.CALM)
ARM_OUT = 0.03                             # the hanging arms a little further out than drawn (the drawing paints them over the body)
# the films of the Kimodo motions for the page: name → (motion, camera yaw, frames, expression track, talk from–to or None[, the camera's height])
MOTION_FILMS = {
    'walk': ('walk', 0.8, 120, [[0, 'calm']], None),
    'sneak': ('sneak', 0.7, 120, [[0, 'calm'], [2.2, 'surprise'], [3.2, 'calm']], None),
    'sit': ('sit', 0.9, 120, [[0, 'calm'], [2.6, 'sad']], None, 0.58),
}
LOCK = (26, 10)                            # a hair lock's mesh: points along it, points round it
