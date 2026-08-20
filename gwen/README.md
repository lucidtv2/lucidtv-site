# GWEN — the review pass

GWEN is two things wearing one name, and that is deliberate.

**Out of fiction,** GWEN is a review pass: a local LLM (Qwen-class, run on your own
machine) reads each finished episode and decides where the hidden layer goes. It runs
before export, costs nothing per episode, and produces the per-platform cuts for you.

**In fiction,** GWEN is what lives in the edit. She is not a character who appears in
episodes; she is the thing that *has been in the room while the episode was assembled*.
The marks she leaves are the Easter-egg layer. The audience is never told she exists.

The joke, which is also the thesis, is that both statements are literally true. The
model really does implant the layer. There really is something in the pipeline putting
things in your videos that you did not consciously choose.

---

## Why this makes editing easier, not harder

This is the design constraint everything else bends around. A hidden-layer project
normally dies because it adds work to every single episode until the creator quietly
stops doing it around episode 30.

GWEN inverts that. The review pass earns its place by doing work you would otherwise
do by hand:

| You used to do this by hand | GWEN does it |
|---|---|
| Scrub the timeline to find the emotional beats worth cutting on | Stage 1 tags every beat with a timecode |
| Decide where to cut for TikTok vs Shorts vs Reels | Stage 2 emits all platform cuts as a plan |
| Export five times with different settings | Stage 3 renders every variant in one command |
| Remember what you did 40 episodes ago | The ledger remembers; you never do |
| Write descriptions, captions, pinned comments | Generated from the plan |

The Easter eggs ride along on work that was already worth doing. If you deleted the
entire hidden layer tomorrow, the pipeline would still be worth running.

**Target: under 15 minutes of added work per episode, and negative added work once
you count the platform exports it replaces.**

---

## The architecture

The single most important rule: **the model decides nothing a rule can decide.**

Local models are unreliable at continuity, arithmetic, and remembering what happened
in episode 12. They are genuinely good at one thing this project needs: reading a
transcript and labelling spans. So that is the only job GWEN gets.

```
  episode master edit
          │
          ▼
  ┌───────────────────┐
  │ STAGE 0  TRANSCRIBE│   whisper.cpp, local, deterministic
  │ → transcript.json  │
  └───────────────────┘
          │
          ▼
  ┌───────────────────┐
  │ STAGE 1  TAG       │   ← the ONLY LLM step
  │ local Qwen model   │     input:  transcript + fixed taxonomy
  │ → tags.json        │     output: [{start, end, tag, confidence}]
  └───────────────────┘     constrained JSON decoding, no prose
          │
          ▼
  ┌───────────────────┐
  │ STAGE 2  PLAN      │   pure Python. no model. no randomness.
  │ gwen_plan.py       │     input:  episode no. + tags + rules + state
  │ → plan.json        │     output: frame-accurate insertion list,
  └───────────────────┘             per platform
          │
          ▼
  ┌───────────────────┐
  │ STAGE 3  RENDER    │   ffmpeg. per-platform variants, captions,
  │ gwen_render.py     │   descriptions, thumbnail pick, marker file
  │ → out/*            │   you can import into your NLE
  └───────────────────┘
          │
          ▼
  ┌───────────────────┐
  │ STAGE 4  VERIFY    │   re-scan the rendered files, confirm each
  │ gwen_verify.py     │   egg survived encode; append to ledger.jsonl
  └───────────────────┘   this is your continuity memory
```

### Why the LLM is boxed into Stage 1

Everything downstream of tagging is arithmetic and lookup, and arithmetic is exactly
where a 7B model will silently betray you. By the time we reach "which egg fires on
episode 137, at what frame, on which platform," there is no judgment left — only a
deterministic function of `(episode_number, tags, rules, state)`.

That gives three properties that matter over a 250-episode run:

1. **Reproducible.** Re-running episode 137 produces byte-identical plans forever.
   Randomness is seeded from the episode number, never from the clock.
2. **Auditable.** When the community claims a pattern exists, you can check whether it
   actually does, because the plan is a file.
3. **Portable.** When today's local model is obsolete in two years, you swap the tagger
   and the entire canon still runs. The lore does not live in the model's head.

---

## Determinism

Nothing in this pipeline may consult the wall clock or an unseeded RNG. Every choice
that looks random to a viewer is `sha256(episode_number + egg_id + salt)` folded into
a float. Same episode in, same layer out, on any machine, in any year.

This is not fussiness. A hidden layer whose pattern cannot be *re-derived* is a hidden
layer the community can never prove, and an unprovable pattern is indistinguishable
from no pattern at all. The audience's ability to solve this depends on it being
mechanically real.

---

## The files

```
gwen/
  README.md               this document
  rules/
    canon.json            the eggs, their triggers, their assets      [from the bible]
    taxonomy.json         the fixed tag vocabulary Stage 1 may emit
    state.json            episode counter + evolving layer state
    ledger.jsonl          append-only record of what actually shipped
  prompts/
    tag.system.md         the Stage 1 system prompt
    tag.schema.json       constrained-decoding schema for the tagger
  tools/
    gwen_plan.py          Stage 2 — deterministic planner
    gwen_render.py        Stage 3 — ffmpeg variant renderer
    gwen_verify.py        Stage 4 — post-encode verification
```

`rules/canon.json` is the only file that carries story. Everything else is machinery.
That separation is what lets the fiction change without touching the pipeline, and the
pipeline change without touching the fiction.

---

## Running a normal episode

```sh
gwen tag    ep=137 master=edits/137.mov     # local model, ~30s
gwen plan   ep=137                          # instant
gwen render ep=137                          # ffmpeg, ~4 min unattended
gwen verify ep=137                          # instant, appends to ledger
```

Apogee episodes (50, 100, 150, 200, 250) use `--apogee`, which unlocks the Tier 3
asset pool and disables the subtlety clamp.

---

## Hardware

Stage 1 is the only step with a model in it, and it is a tagging task on a few hundred
words of transcript. A 7B–14B instruct model with constrained JSON decoding is
sufficient and runs comfortably on consumer hardware. Do not reach for a larger model:
the failure mode you care about is *inconsistency across episodes*, and a small model
pinned to a fixed taxonomy with temperature 0 is more consistent than a large one
improvising.

Set `temperature=0`. Pin the model version and record it in the ledger, so that if
tagging behaviour ever drifts you can see exactly which episode it started on.
