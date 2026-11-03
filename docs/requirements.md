# Requirements

What Pavel said matters, gathered so it isn't lost. Add to it whenever he says something like this; don't drop or
narrow what is here without asking him.

## The goal

- Beautiful, attractive 3D characters for moood's games: as beautiful as in good animated films, organic and exact at
  every degree of stylisation — fine contours, fine forms, a fine look in motion; no broken arms, legs, bones; real
  sizes of body parts. Cartoon is fine; ugly is not. "In small things lies the difference between ugliness and
  attractiveness": polish, manner and precision in the details.
- Faces exact to their reference: every character's face shape, chin, cheekbones, nose (its curve and sharpness),
  mouth (shape, size, where it sits against nose and chin) — different characters have clearly different faces.
- Breadth first, to find the principles of beauty and learn, instrumentally, to make the characters Pavel wants.

## The engine

- It is an engine: few assumptions, much allowed. The agents who write concrete characters have their own vision,
  choose the tools, and are responsible for taste and moderation themselves; the engine doesn't guard them from
  mistakes. Where something can be done two ways that both may be needed (a deformation as body shape or as a pose
  layer), offer both.
- The engine is code; presets are code — examples that show what can be built.
- Built so we can improve any aspect for a long time and make many new versions (also for particular games) without
  breaking the characters.
- Only the right ways, no workarounds, best practices; code review from time to time.
- Where it will live later is not thought about now; we work in this repository and move things later. Don't bring
  up moood's engine or its tools until Pavel does.

- Keep everything we made: the experiment pages, their code and the current gallery stay as they are, running, so
  Pavel can return to them, show them and talk about them. The engine is built beside them, not in their place.

## Motion

- The body moves through the scene only by Kimodo and only along the coordinates Kimodo gives. Never carried
  sideways, never walking on the spot.
- Motions themselves come from Kimodo: touching things (sitting on a chair, leaning, taking an object, hugging),
  turning the body to a target, small life while standing ("a person stands" from Kimodo has it sewn in) — not made
  by formulas, which would make a person look like in a fit. Pavel, softening his first wording: "не понимай меня так
  буквально" — corrections on top of Kimodo's motion (arms kept a little off the body for cloth, a head turn for hair,
  arms kept out of a big head, amplified limbs, a line of action as a pose layer) are allowed.
- Use Kimodo even for small things: looking round, turning back, a head turn — Kimodo turns a head as a person does;
  motions written with sines almost always look unnatural ("все движения, которые ты пишешь синусами, выглядят очень
  плохо"), and I can't see that unnaturalness the way Pavel does. Learn to join Kimodo's motions well. Small life
  (breathing, eye movements) may be by hand if decided from understanding, not from laziness. Kimodo has limits —
  not everything can be asked or joined well — so reasonable departures and artificial corrections are needed
  where it falls short. Best practices.
- Transitions between Kimodo motions without jerks: the next motion made by Kimodo to start from the end of the
  previous one. Contacts with objects the same way, through Kimodo's constraints.
- Clothes are cloth, not a mask on the body: they don't go through the body, they crumple, bend, take the wind, and
  behave logically when a person walks, runs, lies down, tumbles, rolls. Ordinary clothes of today in fabrics of
  different kinds.
- Hair moves with inertia, wind and motion.

## The gallery

- Every path's finals with pictures and animations; clear codes and names to talk by (a letter of the group and a
  number, pictures as «Т5-б»); what belongs to what and what grew from what; an overview to orient by sight.
- Pictures preview on the same page; 3D on the same page, large, without its own scroll, the controls always there:
  turn every model, choose the character, its motions and the rest.
- Runs locally from the repository with `python3 -m http.server`.

## Working

- Look with your own eyes, from several angles; don't show or send results with visible bugs or mediocre ones; if
  an edit doesn't make it better, revert it and try another; don't deliver a version worse than the last.
- Do what is asked, at the level it is asked; don't widen it, don't rush; when Pavel discusses, discuss — don't
  start doing; one question at a time, with its pictures.
- Keep everything Pavel sends (references) and what is discussed in the repository; history always (CLAUDE.md).

## Next, after the engine

Smooth transitions between motions; smooth and combined facial expressions; mouth shapes for speech; a jaw that moves
when speaking (else just the mouth); brows and face during speech; a gaze that follows; blinking and small eye
movements by themselves; speed of cloth and hair for several characters.

## Not now

Breathing and idle life; hands, fingers and grips (Kimodo has none); feet on the ground; contacts with the world;
turning to a target; cartoon timing; scenes.
