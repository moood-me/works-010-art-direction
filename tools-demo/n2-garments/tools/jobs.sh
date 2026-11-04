# GarmentCode designs draped here: name | body | overrides of assets/design_params/default.yaml
# resolution: R=1.6 before a line drapes it coarser (~1/2.5 the points; the CPU here is shared); at > 1.0 GarmentCode
# crashes on garments with a short edge (cuffs, collars), so those stay at its default 1.0. dress-bell ran at 1.0.
# run: bash jobs.sh [--dry] [only-name]   (from anywhere)
GC=/home/user/cache/n2-garments
T=$(dirname "$(readlink -f "$0")")
run() { n=$1; b=$2; shift 2; [ -n "$ONLY" ] && [ "$ONLY" != "$n" ] && return
  [ -z "$DRY" ] && [ -f $GC/runs/${b##*/}/${n}_sim/${n}_sim_sim.obj ] && return   # done already
  args=(); for s in "$@"; do args+=(--set "$s"); done
  (cd $GC/src && PYTHONPATH=. $GC/venv/bin/python $T/gc_run.py --design assets/design_params/default.yaml --body $b --out $GC/runs/${b##*/} --name $n $DRY ${R:+--res $R} "${args[@]}" 2>&1 | grep -v Progress | tail -4); }
DRY=""; [ "$1" = "--dry" ] && { DRY=--dry; shift; }; ONLY=$1
A=$GC/bodies/anny/moood-woman
NOSLV="sleeve.sleeveless=true"
BELL="meta.upper=FittedShirt meta.bottom=SkirtCircle flare-skirt.suns=1.0 flare-skirt.length=0.6 collar.f_collar=CurvyNeckHalf collar.fc_depth=0.6 collar.width=0.3 shirt.strapless=false"
# dresses with designed silhouettes
run dress-bell $A $BELL $NOSLV
# the same at the coarser resolution of its variants (the one above ran into the 50-minute cap at frame 552)
R=1.6 run dress-bell16 $A $BELL $NOSLV
run dress-aline-puff $A meta.upper=FittedShirt meta.bottom=PencilSkirt pencil-skirt.flare=1.5 pencil-skirt.length=0.6 sleeve.sleeveless=false sleeve.length=0.3 sleeve.connect_ruffle=1.8 sleeve.end_width=1.4 sleeve.cuff.type=CuffBand sleeve.cuff.top_ruffle=1.8 collar.f_collar=CircleNeckHalf
run dress-trapeze $A meta.upper=Shirt shirt.length=2.7 shirt.flare=1.5 shirt.width=1.0 sleeve.sleeveless=false sleeve.length=0.25 collar.f_collar=SquareNeckHalf collar.fc_depth=0.5
# a skirt, a shirt with sleeves, trousers
R=1.6 run skirt-circle $A meta.wb=StraightWB meta.bottom=SkirtCircle flare-skirt.suns=0.75 flare-skirt.length=0.45
R=1.6 run pants $A meta.wb=StraightWB meta.bottom=Pants pants.length=0.9 pants.width=1.15 pants.flare=1.0
# one design, its parameters changed
R=1.6 run var-suns03 $A $BELL $NOSLV flare-skirt.suns=0.3
# (suns 1.5 at length 0.85 had not settled in GarmentCode's 50-minute cap here: still spread out — not shown)
R=1.6 run var-suns15-short $A $BELL $NOSLV flare-skirt.suns=1.5 flare-skirt.length=0.35
R=1.6 run var-vneck-short $A $BELL $NOSLV collar.f_collar=VNeckHalf collar.fc_depth=1.4 collar.b_collar=VNeckHalf collar.bc_depth=1.0 flare-skirt.length=0.4
# the tool's own use: one design made to measure on other bodies (GarmentCode's own female and male)
R=1.6 run dress-bell $GC/bodies/gc/mean_female $BELL $NOSLV
# a shirt with long sleeves worn with trousers / with the skirt: GarmentCode makes a top and a bottom as one garment
# sewn at the waistband (the shirt reads as tucked in)
SHIRT="meta.upper=Shirt shirt.length=1.0 shirt.width=1.1 sleeve.sleeveless=false sleeve.length=1.0 sleeve.end_width=0.7 collar.f_collar=VNeckHalf collar.fc_depth=0.8"
R=1.4 run outfit-shirt-pants $A $SHIRT meta.wb=StraightWB meta.bottom=Pants pants.length=0.85 pants.width=1.1
R=1.4 run outfit-shirt-skirt $A $SHIRT meta.wb=StraightWB meta.bottom=SkirtCircle flare-skirt.suns=0.75 flare-skirt.length=0.45
# the tool's own use: random designs from its sampler (tools/sample.py, seed 7), draped on Anny
# (at 1.6 only those two mesh; the others have short edges and would need 1.0: too slow here)
for k in 01 09; do n=rand$k; [ -n "$ONLY" ] && [ "$ONLY" != "$n" ] && continue
  [ -f $GC/runs/moood-woman/${n}_sim/${n}_sim_sim.obj ] && continue
  (cd $GC/src && PYTHONPATH=. $GC/venv/bin/python $T/gc_run.py --design $GC/runs/samples/$n.yaml --body $A --out $GC/runs/moood-woman --name $n --res 1.6 $DRY 2>&1 | grep -v Progress | tail -4); done
# the sewing film: the shirt with the skirt again, its cloth points saved every 4th frame (tools/film.py renders them)
[ -z "$ONLY" -o "$ONLY" = film ] && [ ! -f $GC/runs/film/sewing_sim/sewing_sim_sim.obj ] && (cd $GC/src && PYTHONPATH=. $GC/venv/bin/python $T/gc_run.py --design $GC/runs/moood-woman/outfit-shirt-skirt/design_params.yaml --body $A --out $GC/runs/film --name sewing --res 1.4 --dump $GC/runs/film/frames $DRY 2>&1 | grep -v Progress | tail -3)
