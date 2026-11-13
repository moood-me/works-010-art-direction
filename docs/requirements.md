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

- On "limbs as arcs" (Т5): Pavel never wanted to deform people or bend their limbs. The thought was that even a
  conventional, simple form can convey a real body if it has living, symbolic curves — an explanation of where the
  theme came from, not a rule to bend arms or legs.

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

- Presets matter, presets of parts too. Agents choosing a character's look will look through much of what exists,
  try many, then modify a lot — the engine and presets now, then many games, scenes and characters by other agents.
  Presets must be easy to browse, compare and combine.

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

- From time to time send Pavel pictures in the chat to show progress, even if they look like what he has seen.

- Look with your own eyes, from several angles; don't show or send results with visible bugs or mediocre ones; if
  an edit doesn't make it better, revert it and try another; don't deliver a version worse than the last.
- Do what is asked, at the level it is asked; don't widen it, don't rush; when Pavel discusses, discuss — don't
  start doing; one question at a time, with its pictures.
- Keep everything Pavel sends (references) and what is discussed in the repository; history always (CLAUDE.md).

## The catalogue (Pavel, 2026-11-09 and 10)

What this repository is for from now on, said when the branches were put together.

- Agents will go on writing games, and in them make characters that look good. Different agents in different games
  have their own approaches, particular to the game and to what they mean by it: they are free to.
- They don't reinvent: there is something ready to choose from — taken as it is, or improved.
- Games already written don't change because later agents do something in other games.
- What an agent did that turned out well becomes, more or less, available to the agents after.
- What we have is a set of separate tools. No going mad over generalising them or making any of them fit any other:
  in general that can't be solved and may not be needed; particular approaches are better for the agents to come. But
  the practices that really came out well are there for them to use, change and grow.
- On the shelves lie good practices and good ways of making something — not characters to clone between games.
  Characters may lie there too, but are not taken one to one into another game: at least adapted in how they look.
- What lies there can be run and rendered, and Pavel can look at all of it on the site himself, to talk about it with
  agents: code names to talk by, clear navigation over everything, a catalogue, a list.
- It can grow: agents know where to put their new variants.
- Copied code is no harm. No refactoring into a library for now: a library at once brings the questions of backward
  compatibility and of new versions breaking the old. In the weeks and months to come agents may return and carry the
  really good approaches out into something reusable. What is already a shared module stays one. Common sense: where
  pulling something out clearly makes sense, yes.
- What is clearly unfinished is thrown out. An intermediate result that was good and later grew into something worse
  is kept too.
- Of work still going on (an agent had not finished): nothing is put there; what is finished — a character drawn in a
  style, a character in 3D — is. Taken by character, not by commit.
- The natural heads of main and the engine (very natural, not stylised — Anny's own) are needed beside the drawn heads
  of the 3D characters: some games may need exactly them.
- The engine branch: most of it is not needed — the generalising in it turned out unneeded, and the agent was asked
  not to invent anything new there but did. What of it is good against main and what is not, Pavel can't say yet: he
  and other agents decide later; so do they about quality in general.
- moood, the engine in real games, moving any of this into moood: not thought about now — later.
- Made head-on rather than by inventing: easy, simple, clear.

## Next, after the engine

Smooth transitions between motions; smooth and combined facial expressions; mouth shapes for speech; a jaw that moves
when speaking (else just the mouth); brows and face during speech; a gaze that follows; blinking and small eye
movements by themselves; speed of cloth and hair for several characters.

## After the engine is finished (Pavel, 2026-11-03, going to sleep)

Pavel, 2026-11-04: the two items below (contacts; two people) are not started automatically — only when he asks,
a little later. Now: the engine (hair, clothes). The characters not from Anny (П1 and П2 in one constructor) are not
started automatically either — only when Pavel asks (2026-11-04).

- Motions that come to the right places — a common task. A person walks up to a table and leans on it: the hands
  touch the table; we tell the model, say, a second before the stop the hands must be here, and at the last frame
  still there — the person comes up, leans, holds it about a second. One character comes up to another and puts a
  hand on the shoulder. A character sits down in an armchair standing in the scene, with armrests of a known height,
  puts the hands on the armrests and sits properly. If the model understands some motions badly, never mind — try
  other similar tasks and motions; the main thing is to make the principle work.
- After that, talk with Pavel (a discussion, not a build): how to make two people interact properly — one lifts the
  other in their arms and carries them; A stands, B comes up and touches A's shoulder, A reacts and looks round.

- Two people (Pavel, 2026-11-03): through Kimodo's constraints. One leads, the other follows, the roles change in
  turn; made in parts, by the logic of the script — who reacts to what. The carrier: try by simple means, through
  Kimodo; may be left if too hard. The carried one may be attached — they're moved by the other person's Kimodo
  motion, and that's fine; the rule meant only that people aren't moved by formulas ("не воспринимай меня слишком
  прямо… возможно что-то и ок").
- Reaching to a place: not stretched by formulas afterwards — when we reach, the body leans in, the elbow turns, many
  muscles work. Ask Kimodo to make it right by giving it the right coordinates, as far as possible and easy. An
  idea of direction, not a hard requirement.
- Two people are done for sure, not "if time is left": even what Pavel didn't think through is worked on. B touches
  A's shoulder and A looks round (the hand possibly staying on the turning shoulder); one carries another (comes up,
  bends, lifts, carries, maybe puts down; the carried one attached, posed by Kimodo); if Kimodo understands some
  badly — similar ones (a handshake, a hug, leading by the hand). Checked by numbers (touches, no passing through)
  and by eye; pictures and animations in the gallery; history.
- On the way: find your bearings and use common sense; don't take on overly complex tasks; try to do it well and in
  the spirit of these requirements, as far as possible (Pavel, 2026-11-04).
- Borderline tasks — ones that may take days and still not be done — aren't aimed better than the earlier
  experiments did ("иначе это просто какая-то нереалистичная хрень, которая может делаться ещё 3 дня и в итоге так и
  не сделаться"). E.g. clothes in rolls and lying: О3's level is the target. No new workarounds; old ones removed only
  where that's realistic (Pavel, 2026-11-04).
- Add what Pavel asks to this file, so it isn't lost.

## Not now

Breathing and idle life; fingers and grips (Kimodo has none); feet on the ground; turning to a target; cartoon timing;
scenes. (Contacts of the hands with the world — see above, after the engine.)

## Contacts and two people, tried (Pavel, 2026-11-12)

- The two tasks put off above ("After the engine is finished") are tried now, by Opus agents, in new branches from
  `main`.
- If something is not liked, or could be made better simply, or it is worth the agents trying more — ask them.
- Other scenarios are worth making too: other kinds of objects, other kinds of motions.

## The characters' speed (Pavel, 2026-11-13)

- The question: if the drawn characters built in 3D (Р) are put into a real scene of a game, what will the speed be.
  They should work properly for speed.
- Ideal exactness is not needed there. What is very hard is not forced: "пускай в стену не бьётся".
- The work is done in a branch and a worktree of its own, not poured into `main`.
