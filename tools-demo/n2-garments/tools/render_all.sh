# Render every draped garment that has no picture yet (Blender, Cycles CPU), and copy the meshes to out/.
GC=/home/user/cache/n2-garments; T=$(dirname "$(readlink -f "$0")"); B=/home/user/cache/blender/blender
declare -A COL=([dress-bell]=1f6b5c [dress-bell16]=1f6b5c [dress-aline-puff]=8a3a5c [dress-trapeze]=c8902a [skirt-circle]=2c3a5c
  [shirt-long]=b5523b [pants]=2b3147 [var-suns03]=1f6b5c [var-suns15-long]=1f6b5c [var-sleeve-puff]=1f6b5c
  [outfit-shirt-pants]=e8e2d4/2b3147 [outfit-shirt-skirt]=b5523b/2c3a5c [var-suns15-short]=1f6b5c [var-vneck-short]=1f6b5c [rand01]=6b4a8a [rand09]=3a6b8a [rand10]=8a6b3a)
mkdir -p $GC/renders $GC/out
for d in $GC/runs/[!_]*/*_sim; do n=$(basename $d _sim); body=$(basename $(dirname $d)); o=$d/${n}_sim_sim.obj
  [ -f $o ] || continue
  case $body in moood-woman) bo=$GC/bodies/anny/moood-woman.obj; skin=d9a88a;; *) bo=$GC/bodies/gc/$body.obj; skin=8a8f99;; esac
  for yaw in 20 160; do png=$GC/renders/$body-$n-$yaw.png; [ -f $png ] && continue
    $B -b -P $T/render.py -- $png $bo $skin $o ${COL[$n]:-777777} --yaw $yaw --samples 32 >/dev/null 2>&1; echo $png; done
  # not settled within the 50-minute cap: not given out
  if [ $body = moood-woman ] && [ $n != dress-bell ] && [ $n != var-suns15-long ]; then
    awk '/^v /{printf "v %.6f %.6f %.6f\n",$2/100,$3/100,$4/100; next} /^(f|vt|vn) /' $o > $GC/out/$n.obj
    cp $d/${n}_specification.json $GC/out/$n.specification.json; cp $d/${n}_design_params.yaml $GC/out/$n.design.yaml
  fi
done
cp $GC/bodies/anny/moood-woman.obj $GC/out/body-moood-woman.obj; cp $GC/bodies/anny/moood-woman_map.json $GC/out/body-moood-woman_map.json
cp $GC/bodies/anny/moood-woman.yaml $GC/out/body-moood-woman.yaml
