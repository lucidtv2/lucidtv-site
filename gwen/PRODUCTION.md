# GWEN — production playbook

> **Verify before spending.** I could not confirm current Higgsfield credit pricing,
> Seedance tier limits, or LTX-2 Fast specs against live sources — the research pass
> failed on a session limit and the numbers below are structural estimates, not quoted
> prices. Every figure marked ⚠️ is an assumption. Check them against the actual pricing
> page and re-run the arithmetic before you buy anything. The *allocation logic* holds
> regardless of what the unit costs turn out to be; only the totals move.

---

## 1. The economics that make this possible

The layer runs for 250 episodes on a fixed asset library. Nothing is generated per
episode. This is the single decision that makes a one-person hidden layer survivable —
and it is enforced by the design, not by discipline: the Presence is a silhouette, and a
silhouette can be re-graded, re-cropped, re-timed and re-composited indefinitely without
ever looking like the same shot twice.

**Generate once. Reuse three hundred times.**

A 2-frame appearance from a 4-second clip has ~120 distinct in-points. Six clips × 120
in-points × 5 movement grades × 3 crops is more distinct-looking appearances than the
show will ever need.

---

## 2. The asset bible

| Group | What | Count | Model | Why that model |
|---|---|---:|---|---|
| **Presence — core** | The Notch, static, various distances/angles, 4s | 6 | Higgsfield ⚠️ | Start/end-frame control is what keeps framing consistent across a set; that consistency is the whole asset |
| **Presence — recede** | Walking away, not toward (Law 8), 4s | 4 | Higgsfield ⚠️ | Same |
| **Presence — through** | Gap with something visible in it (Movement IV) | 4 | Seedance ⚠️ | Needs interior detail to hold; higher fidelity earns its cost here |
| **Environment plates** | Empty rooms, corridors, thresholds, 5s loops | 12 | Seedance ⚠️ | Multi-shot coherence; these are backgrounds she is composited into |
| **Glyphs** | 12 nidāna silhouettes + pair renders | 12 | **none — drawn** | Flat vector. Zero credits. Zero drift. Renders identically in year five |
| **LUTs** | 5 movement grades | 5 | **none — colour** | A `.cube` file |
| **Audio** | Interval bed, room tone, the signature | 3 | **none — recorded** | Free and more controllable than generated |
| **Apogee set-pieces** | 30–60s, one per milestone | 5 | Seedance ⚠️ | The only place long-form generation is worth paying for |
| **Divergence ends** | Final-frame cards for the Partition | 8 | **none — stills** | Frame grabs + type |

**Generated assets total: 30 clips + 5 set-pieces.** Everything else costs nothing,
which is deliberate — the free half of the library is the half that has to survive
platform compression, and flat high-contrast art survives it best.

## 3. Credit allocation ⚠️

Assuming a mid-tier generation costs on the order of 10–20 credits for a few seconds —
**verify this** — a ~1000-credit budget allocates roughly:

| Line | Clips | Est. credits | Note |
|---|---:|---:|---|
| Presence core (6) | 6 | 180 | Budget 2–3 attempts each. You will not get the silhouette first try |
| Presence recede (4) | 4 | 120 | |
| Presence through (4) | 4 | 120 | Defer until episode 140 |
| Environment plates (12) | 12 | 180 | Cheaper per unit; less retry pressure |
| Apogee 50 | 1 | 80 | Generate now |
| Apogees 100–250 | 4 | 0 | **Defer.** Years away. Better models will exist |
| **Reserve** | — | **320** | Retries, a deprecated model, a re-shoot of a core asset |

The reserve is not padding. The most likely way this budget fails is one core Presence
clip that never comes out right and eats forty credits in retries — and because the
Presence is the one asset the entire five-year run depends on, that is a fight worth
losing credits to win.

**Draft on LTX Fast, finish on Higgsfield.** ⚠️ Iterate compositions cheaply until the
silhouette reads at 2 frames, *then* spend the expensive generation on the version you
already know works. Most of the retry cost above disappears if you do this.

### Minimum viable launch set

Six Presence core clips, twelve glyphs, five LUTs, three audio beds. That is enough for
episodes 1–50. Everything else can be built while nobody is watching.

---

## 4. Prompt library

Style-lock boilerplate, appended to every Presence generation:

```
high contrast backlit silhouette, single standing human figure, flat black matte,
no facial features, no interior detail, volumetric haze, static locked-off camera,
shallow depth, muted desaturated background, 35mm, grain
```

Negative, every time:

```
face, eyes, hands in focus, text, watermark, logo, camera movement, zoom, dolly,
figure walking toward camera, multiple figures, crowd, gore, distorted anatomy
```

**Presence — core**

1. `Backlit silhouette of a person standing motionless in a doorway at the far end of an empty room, seen from across the room, figure occupies the right third of frame, head area obscured by a soft void of background light, static camera, nothing moves`
2. `Backlit standing silhouette in a corridor, mid-distance, three-quarter turned away from camera, a hand-sized gap of bright background where the head should be, dust in the air, static camera`
3. `Distant silhouette of a standing figure at the end of a long hallway, very small in frame, backlit by a window, head indistinct, absolutely still, static locked camera`
4. `Silhouette of a seated figure facing away, shoulders visible, above the shoulders an empty gap of background, soft window light, motionless, static camera`
5. `Close silhouette of a standing figure's shoulders and upper body filling the left of frame, head region replaced by out-of-focus background light, very shallow depth of field, static camera`
6. `Standing backlit silhouette behind a translucent curtain, softened edges, head area reading as a void, curtain barely moving, otherwise still, static camera`

**Presence — recede** (Law 8: away, never toward)

7. `Backlit silhouette walking slowly away from camera down an empty corridor, head area an indistinct void, figure getting smaller, static locked camera, slow`
8. `Silhouette of a person stepping out of frame to the left, mid-stride, only partially in shot, backlit, head indistinct, static camera`

**Environment plates**

9. `Empty domestic room at dusk, no people, curtains, dust in a shaft of light, static locked-off camera, nothing moves, muted colour, 35mm grain`
10. `Empty institutional corridor, overhead lights, no people, distant doorway, static locked camera, faint air movement`
11. `A doorway seen straight on, dark room beyond, no figure, threshold in sharp focus, static camera`
12. `Empty room with a television playing static, no people, light flickering on the walls, static locked camera`

**Apogee 50 — The First Gate**

13. `Backlit silhouette standing perfectly centred, facing camera, filling the middle of frame, a clean hand-sized void where the head should be, absolutely motionless for the full duration, no camera movement, high contrast, cinematic`

**Apogee 150 — The Defection** (Law 4: the first time the gap faces the viewer)

14. `Backlit standing silhouette centred and facing camera, the void where the head should be glowing faintly from within, motionless, high contrast, static camera` — composite the recursive frame into the gap in post; do not ask a model for it.

---

## 5. Consistency protocol

The Presence must be recognisable in episode 250 as the same thing that appeared in
episode 1, across at least one model deprecation. The design does most of this work
(§4 of the bible), the rest is procedure:

1. **One style-lock frame.** Pick the single best frame from the first successful core
   generation. That image is the reference for every future generation, forever. Save it
   as `presence/STYLE_LOCK.png` and never regenerate it.
2. **Seed discipline.** Record the seed, model, and full prompt for every kept asset in
   `presence/PROVENANCE.md`. Assume you cannot reproduce a generation without it, because
   you cannot.
3. **Silhouette-first QC.** Before keeping any clip: scrub to a random frame, crop to
   vertical, scale to 20% and look at it. If the Notch does not read at that size, the
   clip is unusable no matter how good it looks at full resolution. This test rejects a
   lot of otherwise beautiful generations and it is not negotiable.
4. **Model deprecation is expected.** When a model dies, you re-generate from the
   style-lock frame, not from the prompt. Because the target is a silhouette, a close
   match is achievable in any model — and in the worst case the asset is reproducible by
   hand in a compositor, which is the real reason the design is a silhouette.
5. **Canonise the accident.** When a generation produces an unplanned artifact the
   audience notices, and it does not violate a law, write it into the canon and keep
   doing it deliberately. AI artifacts are the aesthetic; a project that fights its
   tools' failure modes pays twice and looks worse.

---

## 6. The per-episode workflow

```
whisper.cpp  → transcript.json          ~1 min unattended
gwen tag     → tags.json                ~30 s local model
gwen plan    → plan.json                instant
gwen render  → out/{platform}/…         ~4 min unattended
gwen verify  → ledger.jsonl             instant
```

**Attended time: under five minutes.** All of which replaces work that had to happen
anyway — finding beats, cutting per platform, exporting five times, writing descriptions.

The one manual step worth keeping is a thirty-second look at `plan.json` before render,
to confirm the Presence has not landed somewhere absurd. The planner enforces the laws;
it cannot enforce taste.

---

## 7. Folder structure

```
assets/
  presence/
    STYLE_LOCK.png            never regenerate
    PROVENANCE.md             seed + model + prompt for every kept asset
    periphery_m{1..5}_{00..05}.mov
    recede_m{1..5}_{00..03}.mov
    through_m{4..5}_{00..03}.mov
  glyphs/    nidana_{00..11}.png
  luts/      movement_{1..5}.cube
  audio/     interval_{00..02}.wav
  apogee/    50_gate.mov  100_count.mov  150_defection.mov  200_farm.mov
  divergence/ end_{00..07}.png
```

Filenames encode movement and variant so that in two hundred episodes you can still find
*the one where she's in the doorway* without opening a single file.

---

## 8. Failure plans

| When | Do this |
|---|---|
| Credits run out | Stop generating. The launch set covers fifty episodes and the free half of the library covers everything structural. The layer degrades to glyphs, grades, counter and audio — all of which still work |
| A model is deprecated | Regenerate from `STYLE_LOCK.png`, not from the prompt |
| A generation can't be reproduced | It does not matter. Every asset is reused hundreds of times; nothing depends on making a specific clip twice |
| The audience notices an accident | Canonise it (§5.5) |
| Nobody has noticed by episode 30 | Do not escalate early. The layer's value is that it is *already in the past* when the community forms. Escalation is scheduled at 50 for a reason |
| Solved by episode 12 | Also fine, and better than the alternative. The solve is the message, not the mechanism, and the message does not resolve until ~130 no matter how clever anyone is |
| You lose interest | The pipeline still saves you time on every episode. That is why it was built this way |
