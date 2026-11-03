# GarmentCode designs draped here: name | body | overrides of assets/design_params/default.yaml
# RES=1.6 (coarser mesh: ~1/2.5 the points; the CPU here is shared) — used for all but dress-bell
# run: bash jobs.sh [--dry] [only-name]   (from anywhere)
GC=/home/user/cache/n2-garments
T=$(dirname "$(readlink -f "$0")")
run() { n=$1; b=$2; shift 2; [ -n "$ONLY" ] && [ "$ONLY" != "$n" ] && return
  [ -z "$DRY" ] && [ -f $GC/runs/${b##*/}/${n}_sim/${n}_sim_sim.obj ] && return   # done already
  args=(); for s in "$@"; do args+=(--set "$s"); done
  (cd $GC/src && PYTHONPATH=. $GC/venv/bin/python $T/gc_run.py --design assets/design_params/default.yaml --body $b --out $GC/runs/${b##*/} --name $n $DRY ${RES:+--res $RES} "${args[@]}" 2>&1 | grep -v Progress | tail -4); }
DRY=""; [ "$1" = "--dry" ] && { DRY=--dry; shift; }; ONLY=$1
A=$GC/bodies/anny/moood-woman
NOSLV="sleeve.sleeveless=true"
BELL="meta.upper=FittedShirt meta.bottom=SkirtCircle flare-skirt.suns=1.0 flare-skirt.length=0.6 collar.f_collar=CurvyNeckHalf collar.fc_depth=0.6 collar.width=0.3 shirt.strapless=false"
# dresses with designed silhouettes
run dress-bell $A $BELL $NOSLV
run dress-aline-puff $A meta.upper=FittedShirt meta.bottom=PencilSkirt pencil-skirt.flare=1.5 pencil-skirt.length=0.6 sleeve.sleeveless=false sleeve.length=0.3 sleeve.connect_ruffle=1.8 sleeve.end_width=1.4 sleeve.cuff.type=CuffBand sleeve.cuff.top_ruffle=1.8 collar.f_collar=CircleNeckHalf
run dress-trapeze $A meta.upper=Shirt shirt.length=2.7 shirt.flare=1.5 shirt.width=1.0 sleeve.sleeveless=false sleeve.length=0.25 collar.f_collar=SquareNeckHalf collar.fc_depth=0.5
# a skirt, a shirt with sleeves, trousers
run skirt-circle $A meta.wb=StraightWB meta.bottom=SkirtCircle flare-skirt.suns=0.75 flare-skirt.length=0.45
run shirt-long $A meta.upper=Shirt shirt.length=1.25 shirt.width=1.1 sleeve.sleeveless=false sleeve.length=1.0 sleeve.end_width=0.6 collar.f_collar=VNeckHalf collar.fc_depth=0.8
run pants $A meta.wb=StraightWB meta.bottom=Pants pants.length=0.9 pants.width=1.15 pants.flare=1.0
# one design, its parameters changed
run var-suns03 $A $BELL $NOSLV flare-skirt.suns=0.3
run var-suns15-long $A $BELL $NOSLV flare-skirt.suns=1.5 flare-skirt.length=0.85
run var-sleeve-puff $A $BELL sleeve.sleeveless=false sleeve.length=0.25 sleeve.connect_ruffle=2.0 sleeve.end_width=1.6 sleeve.cuff.type=CuffBand
# the tool's own use: one design made to measure on other bodies (GarmentCode's own female and male)
run dress-bell $GC/bodies/gc/mean_female $BELL $NOSLV
run shirt-long $GC/bodies/gc/mean_male meta.upper=Shirt shirt.length=1.25 shirt.width=1.1 sleeve.sleeveless=false sleeve.length=1.0 sleeve.end_width=0.6 collar.f_collar=VNeckHalf collar.fc_depth=0.8
# the tool's own use: random designs from its sampler (tools/sample.py, seed 7), draped on Anny
for k in 01 09 10; do n=rand$k; [ -n "$ONLY" ] && [ "$ONLY" != "$n" ] && continue
  [ -f $GC/runs/moood-woman/${n}_sim/${n}_sim_sim.obj ] && continue
  (cd $GC/src && PYTHONPATH=. $GC/venv/bin/python $T/gc_run.py --design $GC/runs/samples/$n.yaml --body $A --out $GC/runs/moood-woman --name $n $DRY ${RES:+--res $RES} 2>&1 | grep -v Progress | tail -4); done
