#!/bin/sh
# The page's pictures from the shots: O = shot.mjs output, V = vrmshot.mjs output
set -e
O=${1:-/home/user/cache/n6-toon/out}; V=${2:-/home/user/cache/n6-toon/vout}
HERE=$(cd "$(dirname "$0")" && pwd); P="$HERE/../pics"; S="python3 $HERE/sheet.py"
mkdir -p "$P"
# the toon trio: cut to the figures
for f in "$O"/p-three-*.png; do python3 -c "import sys;from PIL import Image;Image.open(sys.argv[1]).crop((120,80,1080,680)).save(sys.argv[2])" "$f" "${f%.png}.crop.png"; done

# ours alone, for the 'now' side
$S "$P/heads-now.webp" 3 400 "$O/g-anime-tq-ours.png|аниме-девушка" "$O/g-red-tq-ours.png|рыжая девушка" "$O/g-hood-side-ours.png|женщина в капюшоне"
# shade: hard and soft
$S "$P/shade-anime.webp" 2 500 "$O/g-anime-tq-ours.png|наш тун" "$O/g-anime-tq-hard.png|MToon жёсткая, наш свет" "$O/g-anime-tq-hard+one.png|MToon жёсткая, один свет" "$O/g-anime-tq-soft+one.png|MToon мягкая, один свет"
$S "$P/shade-red.webp" 2 500 "$O/g-red-tq-ours.png|наш тун" "$O/g-red-tq-hard.png|MToon жёсткая, наш свет" "$O/g-red-tq-hard+one.png|MToon жёсткая, один свет" "$O/g-red-tq-soft+one.png|MToon мягкая, один свет"
# shade colour
$S "$P/tint-heads.webp" 3 400 "$O/g-anime-tq-ours.png|наш тун" "$O/g-anime-tq-hard+one.png|тень темнее того же цвета" "$O/g-anime-tq-tint+one.png|тень своего цвета (тёплая)" "$O/g-hood-side-ours.png|наш тун" "$O/g-hood-side-hard+one.png|тень темнее того же цвета" "$O/g-hood-side-tint+one.png|тень своего цвета (тёплая)"
# rim and matcap
$S "$P/rim-heads.webp" 2 500 "$O/g-red-tq-ours.png|наш тун" "$O/g-red-tq-rim+one.png|MToon: ободок + маткап" "$O/g-hood-side-ours.png|наш тун" "$O/g-hood-side-rim+one.png|MToon: ободок + маткап"
# outline widths
$S "$P/outline-anime.webp" 2 500 "$O/g-anime-tq-thin+one.png|0,7 мм в мире" "$O/g-anime-tq-tint+one.png|1,8 мм в мире" "$O/g-anime-tq-thick+one.png|5 мм в мире" "$O/g-anime-tq-screen+one.png|по экрану"
$S "$P/outline-toon.webp" 2 700 "$O/p-three-thin+one.crop.png|2 мм в мире" "$O/p-three-tint+one.crop.png|6 мм в мире (как наш)" "$O/p-three-thick+one.crop.png|16 мм в мире" "$O/p-three-screen+one.crop.png|по экрану"
# the toon cast
$S "$P/toon-now.webp" 1 900 "$O/p-three-ours.crop.png|наш тун с контуром (П2, v2)"
$S "$P/toon-mtoon.webp" 2 700 "$O/p-three-hard.crop.png|MToon жёсткая, наш свет" "$O/p-three-hard+one.crop.png|жёсткая, один свет" "$O/p-three-soft+one.crop.png|мягкая, один свет" "$O/p-three-tint+one.crop.png|тень своего цвета" "$O/p-three-rim+one.crop.png|ободок + маткап" "$O/p-three-screen+one.crop.png|контур по экрану"
# the engine's body
$S "$P/body-now.webp" 2 400 "$O/d-woman-ours.png|движок: гладкий свет" "$O/d-woman-face-ours.png|вблизи"
$S "$P/body-mtoon.webp" 3 400 "$O/d-woman-hard+one.png|MToon жёсткая" "$O/d-woman-soft+one.png|мягкая" "$O/d-woman-tint+one.png|тень своего цвета" "$O/d-woman-face-hard+one.png|вблизи: жёсткая" "$O/d-woman-face-soft+one.png|вблизи: мягкая" "$O/d-woman-face-rim+one.png|вблизи: ободок + маткап"
# what MToon is for: VRM avatars as their authors set them
$S "$P/use-avatars.webp" 2 500 "$V/v-seed-full-mtoon.png|Seed-san (VirtualCast)" "$V/v-seed-bust-mtoon.png|вблизи" "$V/v-twist-full-mtoon.png|пример pixiv (VRM 1.0)" "$V/v-twist-bust-mtoon.png|вблизи"
$S "$P/use-what-it-adds.webp" 3 400 "$V/v-twist-bust-mtoon.png|MToon, как задал автор" "$V/v-twist-bust-nooutline.png|без контура" "$V/v-twist-bust-plain.png|обычный материал" "$V/v-seed-bust-mtoon.png|MToon, как задал автор" "$V/v-seed-bust-nooutline.png|без контура" "$V/v-seed-bust-plain.png|обычный материал"
cp "$V/v-twist-turn.mp4" "$P/use-turn.mp4"
du -sh "$P"
