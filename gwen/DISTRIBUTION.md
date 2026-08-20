# GWEN — the Partition

> **Verify before relying on it.** Platform behaviour around near-duplicate cross-posting,
> watermark penalties, and transcode aggressiveness changes constantly, and the research
> pass that was meant to confirm current specifics failed on a session limit. Items marked
> ⚠️ are reasoning from durable engineering facts (bitrate, compression, aspect ratio),
> not from a checked 2026 policy page. The structure survives either way; the routing
> might need adjusting.

---

## 1. Why the split is real

The Partition works because it is an **engineering fact before it is a narrative one.**

Each platform gets the payload its encoding is actually good at. TikTok gets the glyphs
because glyphs are flat high-contrast silhouettes and that is the only class of image
that reliably survives an aggressive transcode ⚠️. YouTube-long gets the audio layer
because it is the only channel with the bitrate to carry it ⚠️. Reels gets the counter
because legible overlay text in the safe area is what it handles well.

This matters more than it sounds. A split invented purely for the fiction ("the TikTok
one has a secret!") reads as marketing and collapses the moment someone asks why. A split
that falls out of what each codec destroys is *defensible on technical grounds*, which
means the creator can explain it honestly, in public, without ever revealing anything.

| Channel | Carries | Lacks |
|---|---|---|
| YouTube long | Full essay · audio layer · counter | Glyphs, divergent ending |
| YouTube Shorts | A different final frame | Audio layer, counter |
| TikTok | Glyph frames · Presence | Audio layer, counter |
| Instagram Reels | The counter · Presence holds | Glyphs, audio layer |
| X / Threads / Bluesky | Caption-layer text fragments | All video payload |
| lucidtv site | **The index** — the only place an assembly can be checked | Everything else |

Plus the rotating **carrier**: each episode mints one fragment and hands it to exactly
one platform, on a stride coprime with the platform count. Following a single account
never yields a complete record. Assembly requires trading; trading requires a community.

---

## 2. The realisation moment

The most important beat in the first fifty episodes is the first side-by-side post.
Engineer it. Do not hope for it.

**Episode 23** ships with an unmissable divergence — the TikTok cut ends on a glyph, the
YouTube cut ends on black. Not subtle, not deniable, and the kind of thing exactly one
person notices and immediately posts about.

**Episode 25** contains a Tier 2 event that only parses if you saw *both* endings.
Everyone who caught the side-by-side gets private, unmistakable confirmation that the
difference was deliberate. Everyone else watches those people get excited about something
they cannot see.

That asymmetry is the recruiting mechanism. It converts a passive viewer into a person
who checks the other platform — which is the exact behaviour the whole distribution
scheme exists to produce, and, not incidentally, the exact behaviour the show is about.

---

## 3. Silent confirmation

A decoding community dies without a confirmation loop. Solvers must be able to *know*
they are right. But the creator confirming anything ends the project.

The resolution is §6 of the bible: **the counter is a real running total.** Anyone
patient enough to count tagged moments across every episode can check that the arithmetic
closes. When it does, they know — with certainty, verifiable independently, without a
single word from the creator.

The site's index is the second loop. It is a static page with no backend: a viewer types
their assembled string, the page hashes it in-browser and compares against a stored
digest. Match reveals the next thing. No server, no analytics, no creator involvement.

```js
// The whole mechanism. Plain static HTML — no backend, and nothing to leak.
const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(guess.trim().toUpperCase()));
const hex = [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
if (hex === KNOWN) reveal();
```

Everything else the site can carry costs nothing and is pure texture: an HTML comment
that changes with the episode count, a `robots.txt` disallowing a path that exists, a 404
page that is not empty.

---

## 4. Deniability

The posture is **never confirm, never deny, only say true things.**

This is survivable for five years because of the convergence (§1 of the bible): every
honest answer is also the secret. "A local model helps me edit." True. Complete.
Unbelievable. The project never has to lie, which is the only reason it can be sustained
by one person under sustained questioning.

The one circumstance that overrides this: if someone appears genuinely unable to tell
fiction from reality, break character privately and kindly. The bit is never worth a
person. (Ethics charter §5.)

---

## 5. The first fifty episodes

**Nobody is watching. That is the opportunity, not the problem.**

This is the only window the project will ever get to lay a hundred pieces of evidence in
plain sight, unobserved, so that when the community forms and goes back through the
archive, the past is already dense with her. Build the past first — it is the only part
that cannot be added later.

| Episodes | The layer does | The audience |
|---|---|---|
| 1–10 | Tier 0 and 1 only. Counter, grade, one Presence per episode, glyphs begin | Nothing. Nobody notices. Correct |
| 11–22 | `presence.hold` begins on primes. Density unchanged | A first "did anyone else see" comment, probably ignored |
| **23** | **The divergence.** TikTok ends on a glyph, YouTube on black | Someone posts a side-by-side |
| **25** | The Tier 2 event that needs both endings | The first people who *know*. The community's founding members |
| 26–40 | Hold steady. Do not escalate | Theories. Wrong ones. Let them be wrong |
| 41–49 | Nothing changes. Resist the urge | Tension, if it is working. Silence, if it is not. Both are fine |
| **50** | **The First Gate.** Three seconds, centred, undeniable | Everyone. Then the archive rewatch begins |

### Contingencies

**Nobody noticed by episode 30.** Do not escalate. Episode 50 is designed to be
impossible to miss, and its power comes entirely from forty-nine episodes of accumulated
evidence sitting there waiting to be found. Escalating early spends the archive to buy
attention you would have got anyway.

**Solved by episode 12.** Fine — better than the alternative. The mechanism is not the
secret. Someone who works out that glyphs are being emitted has found a cipher whose
message does not complete until ~130 and whose meaning does not land until 250. Let them
have the mechanism. They will stay for the message.

---

## 6. Weekly rhythm

Five episodes a week, one person, sustainable:

| | Mon | Tue | Wed | Thu | Fri |
|---|---|---|---|---|---|
| Long essay (YT) | ● | | ● | | |
| Shorts / TikTok / Reels | ● | ● | ● | ● | ● |
| Text channels | | ● | | ● | |
| Carrier rotates | → | → | → | → | → |

The carrier rotation is handled by the planner. Nothing here requires the creator to
remember anything.

---

## 7. Episode 187 for a first-time viewer

Non-negotiable, and the place most lore projects quietly fail: **every episode is a
complete essay about mind, meaning and the moving image.** That is the actual show. The
layer is underneath and never load-bearing for comprehension.

A first-time viewer at 187 gets: a good standalone essay, an odd colour grade, a number
in the corner during a silence, and possibly two frames of something in the right third
of the frame that they are not sure they saw.

That last thing is the hook, and it works *because* they have no context — "what was
that" is a stronger first impression than any amount of accumulated lore, and it is the
one experience the layer can deliver identically at episode 3 and episode 187.

Then they scroll the comments, where four hundred people are discussing something with
total seriousness and no explanation, and the archive is right there.

---

## 8. Metrics

Watch four things:

| Signal | Means | Rough target by ep 50 |
|---|---|---|
| Cross-platform comment overlap | The Partition is working | Any at all |
| Frame-by-frame / screenshot posts | Tier 1 is landing | >5 organic |
| Rewatch rate on old episodes after an apogee | The archive is dense enough | Measurable spike at 50 |
| Community home base exists and is not creator-run | The hunt is self-sustaining | Exists by ep 60 |

If the fourth never happens, the project is a well-made essay channel with a private
layer in it — which is a perfectly good outcome, and the pipeline still pays for itself
every week.
