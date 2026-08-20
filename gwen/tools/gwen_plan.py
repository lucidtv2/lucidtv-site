#!/usr/bin/env python3
"""GWEN Stage 2 — the planner.

Turns (episode number, Stage 1 tags, canon rules, layer state) into a frame-accurate,
per-platform insertion plan.

There is no model in this file and there never will be. Every choice that looks random
to a viewer is derived from a hash of the episode number, so the same episode always
produces the same plan, on any machine, in any year. That is what makes the hidden
layer *provable* — a pattern the audience cannot re-derive is indistinguishable from
no pattern at all.

    python3 gwen_plan.py --ep 137 --tags tags.json --out plan.json

Reads rules/canon.json, rules/taxonomy.json and rules/state.json relative to the
gwen/ directory unless overridden.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gwen_message  # noqa: E402  (same directory; the cipher lives next door)

GWEN_DIR = Path(__file__).resolve().parent.parent
FPS_DEFAULT = 30
SILENCE_MIN_SECONDS = 1.2


# ---------------------------------------------------------------- determinism


def stream(*parts: Any) -> float:
    """A stable float in [0, 1) derived from the given parts.

    Never seeded from the clock. Two runs of the same episode agree forever, which is
    the whole basis of the audience being able to prove the layer exists.
    """
    joined = "\x1f".join(str(p) for p in parts)
    digest = hashlib.sha256(joined.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def pick(seq: list, *parts: Any):
    """Deterministically choose one element of seq."""
    if not seq:
        return None
    return seq[int(stream(*parts) * len(seq)) % len(seq)]


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    f = 3
    while f * f <= n:
        if n % f == 0:
            return False
        f += 2
    return True


# ---------------------------------------------------------------- data model


@dataclass
class Insertion:
    egg_id: str
    role: str
    tier: int
    asset: str | None
    start_frame: int
    duration_frames: int
    region: str
    platforms: list[str]
    reason: str
    meaning: str = ""
    glyphs: list[int] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Plan:
    episode: int
    fps: int
    apogee: bool
    rules_version: int
    insertions: list[Insertion] = field(default_factory=list)
    platform_fragments: dict[str, str] = field(default_factory=dict)
    counter: int = 0
    glyphs_emitted_after: int = 0
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "episode": self.episode,
            "fps": self.fps,
            "apogee": self.apogee,
            "rules_version": self.rules_version,
            "counter": self.counter,
            "platform_fragments": self.platform_fragments,
            "glyphs_emitted_after": self.glyphs_emitted_after,
            "insertions": [i.as_dict() for i in self.insertions],
            "notes": self.notes,
        }


# ---------------------------------------------------------------- tag loading


def load_tags(path: Path, taxonomy: dict, fps: int) -> list[dict]:
    """Load Stage 1 output, discard anything the tagger should not have said, and
    synthesise SILENCE spans mechanically from the gaps."""
    raw = json.loads(path.read_text())
    allowed = {t["id"] for t in taxonomy["tags"]} - {"SILENCE"}

    tags: list[dict] = []
    for item in raw:
        tag = item.get("tag")
        if tag not in allowed:
            # Covers both hallucinated labels and a model that emitted SILENCE
            # despite being told not to.
            continue
        if float(item.get("confidence", 0.0)) < 0.6:
            continue
        tags.append(
            {
                "tag": tag,
                "start": float(item["start"]),
                "end": float(item["end"]),
                "confidence": float(item.get("confidence", 1.0)),
            }
        )

    tags.sort(key=lambda t: t["start"])

    # SILENCE is computed, never judged. A gap of >= 1.2s between spoken segments.
    silences = []
    for prev, nxt in zip(tags, tags[1:]):
        gap = nxt["start"] - prev["end"]
        if gap >= SILENCE_MIN_SECONDS:
            silences.append(
                {
                    "tag": "SILENCE",
                    "start": prev["end"],
                    "end": nxt["start"],
                    "confidence": 1.0,
                }
            )
    tags.extend(silences)
    tags.sort(key=lambda t: t["start"])
    return tags


# ---------------------------------------------------------------- triggering


def trigger_fires(egg: dict, ep: int, tags: list[dict], apogee: bool) -> list[dict]:
    """Return the list of tag-spans this egg should attach to, or a single synthetic
    span for episode-level eggs. Empty list means the egg does not fire."""
    trig = egg["trigger"]
    kind = trig["type"]

    lo = trig.get("from_episode", 1)
    hi = trig.get("to_episode")
    if ep < lo or (hi is not None and ep > hi):
        return []

    if egg.get("tier") == 3 and not apogee:
        return []

    if kind == "always":
        return [{"tag": "*", "start": 0.0, "end": 0.0, "confidence": 1.0}]

    if kind == "every_n":
        n = trig["n"]
        offset = trig.get("offset", 0)
        return [{"tag": "*", "start": 0.0, "end": 0.0, "confidence": 1.0}] if (ep - offset) % n == 0 else []

    if kind == "prime":
        return [{"tag": "*", "start": 0.0, "end": 0.0, "confidence": 1.0}] if is_prime(ep) else []

    if kind == "milestone":
        return [{"tag": "*", "start": 0.0, "end": 0.0, "confidence": 1.0}] if ep % trig.get("n", 50) == 0 else []

    if kind == "on_tag":
        want = trig["tag"]
        floor = trig.get("min_confidence", 0.6)
        hits = [t for t in tags if t["tag"] == want and t["confidence"] >= floor]

        # Pacing gate. Some eggs must not fire every time their tag appears — the
        # message has to take 150 episodes to assemble, not 60. Deterministic, so the
        # skipped episodes are still a fixed fact about the run rather than a coin flip.
        pace = trig.get("pace")
        if pace is not None and stream("pace", ep, egg["id"]) >= pace:
            return []

        cap = trig.get("max_per_episode", 1)
        if len(hits) > cap:
            # Choose deterministically rather than taking the first, so the layer is
            # not trivially "always the earliest mention".
            hits.sort(key=lambda t: stream("select", ep, egg["id"], t["start"]))
            hits = hits[:cap]
            hits.sort(key=lambda t: t["start"])
        return hits

    if kind == "probability":
        p = trig["p"]
        return [{"tag": "*", "start": 0.0, "end": 0.0, "confidence": 1.0}] if stream("fire", ep, egg["id"]) < p else []

    raise ValueError(f"unknown trigger type: {kind!r} on egg {egg['id']!r}")


# ---------------------------------------------------------------- escalation


def movement_of(ep: int, rules: dict) -> dict:
    """Which of the five 50-episode movements this episode belongs to."""
    for m in rules.get("movements", []):
        lo, hi = m["episodes"]
        if lo <= ep <= hi:
            return m
    return {"n": 0, "name": "unmapped", "grade": "natural", "gap": "none"}


def scaled_duration(egg: dict, ep: int) -> int:
    """Egg duration grows across the run — the layer becomes less deniable as the
    audience becomes more capable of seeing it. Expressed as 'linear:a..b@N'."""
    place = egg["placement"]
    base = int(place.get("duration_frames", 3))
    spec = egg.get("escalation", {}).get("duration_scale")
    if not spec or not spec.startswith("linear:"):
        return base
    body = spec.split(":", 1)[1]
    span, end_ep = body.split("@")
    a, b = (int(x) for x in span.split(".."))
    end_ep = int(end_ep)
    t = min(max(ep / end_ep, 0.0), 1.0)
    return max(1, round(a + (b - a) * t))


# ---------------------------------------------------------------- fragments


def assign_fragments(ep: int, rules: dict) -> dict[str, str]:
    """No single platform ever carries the whole thing.

    Each episode mints a fragment; the platform that receives it rotates on a stride
    coprime with the platform count, so a viewer watching only one platform gets a
    complete-looking but lacunose record, and assembly requires trading. The stride
    is what makes "just follow them everywhere" not equal to "watch one and wait".
    """
    platforms = rules["platforms"]
    n = len(platforms)
    stride = rules.get("fragment_stride", 3)
    carrier = platforms[(ep * stride) % n]
    decoy = platforms[(ep * stride + 1) % n]
    return {
        "carrier": carrier,
        "decoy": decoy,
        "fragment_id": f"F{ep:04d}",
    }


# ---------------------------------------------------------------- planning


def build_plan(ep: int, tags: list[dict], rules: dict, state: dict, fps: int, apogee: bool) -> Plan:
    # Boxed so the nested insertion loop can advance it. The message pointer is the
    # one piece of genuine cross-episode state the planner carries.
    glyphs_emitted = [int(state.get('message', {}).get('emitted', 0))]
    plan = Plan(
        episode=ep,
        fps=fps,
        apogee=apogee,
        rules_version=rules.get("version", 1),
        counter=state.get("counter_base", 0) + ep,
    )

    movement = movement_of(ep, rules)
    plan.notes.append(f"movement {movement['n']} — {movement['name']} (grade: {movement['grade']}, gap: {movement['gap']})")

    if ep in rules.get("silent_episodes", []):
        # Law 10. The layer's loudest act is its absence, and it is enforced here
        # rather than left to the creator to remember in five years' time.
        plan.notes.append(
            "LAW 10 — SILENT EPISODE. Nothing fires. This is not a bug and must not "
            "be 'fixed'. The plan is empty on purpose."
        )
        plan.platform_fragments = {"carrier": "none", "decoy": "none", "fragment_id": "—"}
        return plan

    subtlety_clamp = not apogee
    max_tier = 3 if apogee else int(rules.get("max_tier_normal", 2))

    for egg in rules["eggs"]:
        if egg.get("tier", 0) > max_tier:
            continue

        spans = trigger_fires(egg, ep, tags, apogee)
        if not spans:
            continue

        for span in spans:
            place = egg["placement"]
            anchor = place.get("anchor", "tag_start")

            if anchor == "tag_start":
                anchor_frame = int(round(span["start"] * fps))
            elif anchor == "tag_end":
                anchor_frame = int(round(span["end"] * fps))
            elif anchor == "tag_mid":
                anchor_frame = int(round(((span["start"] + span["end"]) / 2) * fps))
            elif anchor == "absolute":
                anchor_frame = int(place.get("frame", 0))
            else:
                raise ValueError(f"unknown anchor {anchor!r} on egg {egg['id']!r}")

            start_frame = anchor_frame + int(place.get("offset_frames", 0))
            if not (anchor == "absolute" and int(place.get("frame", 0)) < 0):
                # A negative absolute frame means "counted back from the end" and is
                # resolved by the renderer, which knows the duration. Everything else
                # clamps at zero.
                start_frame = max(0, start_frame)

            duration = scaled_duration(egg, ep)
            if subtlety_clamp and egg.get("role") == "presence":
                # The clamp exists to keep HER deniable outside apogees. It has no
                # business truncating the counter or the audio bed, which are supposed
                # to be readable.
                duration = min(duration, int(rules.get("subtlety_clamp_frames", 8)))

            asset = None
            if egg.get("asset"):
                variants = int(egg.get("variants", 1))
                if egg.get("sequence") == "message":
                    # Deliberately NOT assigned here. The message stream has to follow
                    # the order a viewer actually sees the glyphs in, which is frame
                    # order — not the order the eggs happen to sit in canon.json. If
                    # it were assigned here, an episode carrying both a single and a
                    # pair would emit them scrambled and the message would never
                    # resolve. Assignment happens in the post-sort pass below.
                    v = 0
                else:
                    v = int(stream("variant", ep, egg["id"], span["start"]) * variants) % variants
                if asset is None:
                    asset = egg["asset"].replace("{v}", f"{v:02d}")
                asset = asset.replace("{m}", str(movement["n"]))

            platforms = egg.get("platforms", rules["platforms"])
            if egg.get("platform_mode") == "carrier_only":
                platforms = [assign_fragments(ep, rules)["carrier"]]
            elif egg.get("platform_mode") == "all_but_carrier":
                carrier = assign_fragments(ep, rules)["carrier"]
                platforms = [p for p in rules["platforms"] if p != carrier]

            plan.insertions.append(
                Insertion(
                    egg_id=egg["id"],
                    role=egg.get("role", "overlay"),
                    tier=egg.get("tier", 0),
                    asset=asset,
                    start_frame=start_frame,
                    duration_frames=duration,
                    region=place.get("region", "full"),
                    platforms=platforms,
                    reason=f"{egg['trigger']['type']}"
                    + (f" on {span['tag']}@{span['start']:.2f}s" if span["tag"] != "*" else ""),
                    meaning=egg.get("meaning", ""),
                )
            )

    plan.insertions.sort(key=lambda i: (i.start_frame, i.egg_id))

    # The message stream, assigned strictly in the order a viewer encounters the
    # glyphs. What the community concatenates is a flat glyph sequence read in pairs,
    # so the only thing that has to be right is the ORDER.
    for ins in plan.insertions:
        if ins.role != "glyph":
            continue
        count = 2 if "pair" in ins.egg_id else 1
        ins.glyphs = [gwen_message.glyph_for(glyphs_emitted[0] + k) for k in range(count)]
        glyphs_emitted[0] += count
        stem = ins.asset.rsplit("_", 1)[0] if ins.asset else "glyphs/nidana"
        ins.asset = stem + "_" + "-".join(f"{g:02d}" for g in ins.glyphs) + ".png"

    # LAW 5 — she is never in two places in one episode.
    #
    # This has to be enforced here rather than trusted to the rules, because two eggs
    # with unrelated triggers (a tag-anchored one and a prime-episode one) will
    # eventually collide on their own, and when they do the layer stops looking like a
    # presence and starts looking like a glitch. Highest tier wins; ties go to the
    # earlier appearance.
    presences = [i for i in plan.insertions if i.role == "presence"]
    if len(presences) > 1:
        keep = sorted(presences, key=lambda i: (-i.tier, i.start_frame))[0]
        for dropped in presences:
            if dropped is not keep:
                plan.insertions.remove(dropped)
        plan.notes.append(
            f"LAW 5 — kept {keep.egg_id}@{keep.start_frame}, dropped "
            f"{', '.join(sorted(d.egg_id for d in presences if d is not keep))}"
        )

    plan.platform_fragments = assign_fragments(ep, rules)
    plan.glyphs_emitted_after = glyphs_emitted[0]

    density = len(plan.insertions)
    ceiling = int(rules.get("max_insertions_per_episode", 9))
    if density > ceiling:
        # Too many eggs reads as noise, not signal, and noise is unsolvable. Drop the
        # lowest tiers first — the deniable ones are the ones we can afford to lose.
        plan.insertions.sort(key=lambda i: (i.tier, -i.start_frame))
        dropped = plan.insertions[: density - ceiling]
        plan.insertions = plan.insertions[density - ceiling :]
        plan.insertions.sort(key=lambda i: (i.start_frame, i.egg_id))
        plan.notes.append(
            f"density clamp: dropped {len(dropped)} low-tier insertions "
            f"({', '.join(sorted({d.egg_id for d in dropped}))})"
        )

    if apogee:
        plan.notes.append("APOGEE episode — Tier 3 unlocked, subtlety clamp disabled.")

    return plan


# ---------------------------------------------------------------- entrypoint


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="GWEN Stage 2 planner")
    ap.add_argument("--ep", type=int, required=True, help="episode number")
    ap.add_argument("--tags", type=Path, required=True, help="Stage 1 tags.json")
    ap.add_argument("--rules", type=Path, default=GWEN_DIR / "rules" / "canon.json")
    ap.add_argument("--taxonomy", type=Path, default=GWEN_DIR / "rules" / "taxonomy.json")
    ap.add_argument("--state", type=Path, default=GWEN_DIR / "rules" / "state.json")
    ap.add_argument("--fps", type=int, default=FPS_DEFAULT)
    ap.add_argument("--apogee", action="store_true", help="force apogee mode")
    ap.add_argument("--glyphs-emitted", type=int, default=None,
                    help="override the message pointer (default: from state.json)")
    ap.add_argument("--out", type=Path, default=Path("plan.json"))
    args = ap.parse_args(argv)

    rules = json.loads(args.rules.read_text())
    taxonomy = json.loads(args.taxonomy.read_text())
    state = json.loads(args.state.read_text()) if args.state.exists() else {}

    if args.glyphs_emitted is not None:
        state.setdefault("message", {})["emitted"] = args.glyphs_emitted

    apogee = args.apogee or (args.ep % int(rules.get("apogee_interval", 50)) == 0)
    tags = load_tags(args.tags, taxonomy, args.fps)
    plan = build_plan(args.ep, tags, rules, state, args.fps, apogee)

    args.out.write_text(json.dumps(plan.as_dict(), indent=2) + "\n")

    print(f"episode {args.ep}: {len(plan.insertions)} insertions"
          f"{' [APOGEE]' if apogee else ''}, "
          f"carrier={plan.platform_fragments['carrier']}", file=sys.stderr)
    for note in plan.notes:
        print(f"  note: {note}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
