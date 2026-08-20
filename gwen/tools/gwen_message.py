#!/usr/bin/env python3
"""The twelve-glyph cipher.

The alphabet is the twelve nidanas of dependent origination, in bhavacakra order.
Twelve symbols means base twelve, which is the only reason this cipher exists in this
form: the encoding had to be hand-decodable with a pencil, and it had to teach the
source material to anyone who looked up what the pictures were.

    plaintext -> A1Z26 -> base 12 -> glyph indices 0..11

Space is glyph 0, which is also the separator, which is also the empty house. That is a
coincidence and it is a good one.

    python3 gwen_message.py --preview
    python3 gwen_message.py --schedule 150
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GWEN_DIR = Path(__file__).resolve().parent.parent

# Bhavacakra order. Index is the base-12 digit; the name is what the viewer sees.
NIDANA = [
    "empty-house",      # 0  — salayatana, the six sense-gates. Also the space character.
    "blind-man",        # 1  — avidya, ignorance
    "potter",           # 2  — samskara, formation
    "monkey",           # 3  — vijnana, consciousness
    "boat",             # 4  — namarupa, name-and-form
    "embrace",          # 5  — sparsa, contact
    "arrow-in-eye",     # 6  — vedana, feeling
    "drinker",          # 7  — trsna, craving
    "plucking-fruit",   # 8  — upadana, grasping
    "pregnant-woman",   # 9  — bhava, becoming
    "birth",            # 10 — jati
    "corpse-borne",     # 11 — jaramarana, ageing and death
]


def encode(plaintext: str) -> list[int]:
    """Text to a flat list of base-12 glyph indices, two glyphs per character.

    Fixed width, always. A variable-width encoding is smaller and completely broken:
    with space as 0 and A as 1, the glyph 1 is ambiguous between the letter A and the
    leading digit of a two-digit number, so WAS encodes to 1,11,1,1,7 and decodes to
    WMG. There is no context rule that resolves this reliably, and a cipher the
    creator cannot decode is a cipher the audience certainly cannot.

    Two glyphs per character costs twice the episodes and buys an encoding that is
    unambiguous, trivially hand-decodable in pairs, and consistent with glyph.pair
    emitting exactly one letter.
    """
    out: list[int] = []
    for ch in plaintext.upper():
        if ch == " ":
            n = 0
        elif "A" <= ch <= "Z":
            n = ord(ch) - ord("A") + 1      # A1Z26, so 1..26
        else:
            continue
        out.append(n // 12)
        out.append(n % 12)
    return out


def decode(glyphs: list[int]) -> str:
    """Inverse, for verifying a community solution actually resolves."""
    out = []
    for i in range(0, len(glyphs) - 1, 2):
        n = glyphs[i] * 12 + glyphs[i + 1]
        if n == 0:
            out.append(" ")
        elif 1 <= n <= 26:
            out.append(chr(ord("A") + n - 1))
    return "".join(out)


def load_message() -> tuple[str, list[int]]:
    state = json.loads((GWEN_DIR / "rules" / "state.json").read_text())
    plaintext = state["message"]["plaintext"]
    return plaintext, encode(plaintext)


def glyph_for(emitted_count: int) -> int:
    """The glyph this firing should carry, given how many have already gone out.

    Sequential, NOT hashed. A hashed glyph would emit a pretty random symbol every
    episode and assemble into nothing, which would make the Episode 150 payoff a lie.
    The community must be able to concatenate what they collected, in order, and have
    it resolve.
    """
    _, glyphs = load_message()
    return glyphs[emitted_count % len(glyphs)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="GWEN twelve-glyph cipher")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--schedule", type=int, metavar="N",
                    help="show the emission schedule assuming a firing rate")
    ap.add_argument("--rate", type=float, default=0.6,
                    help="fraction of episodes in which glyph.single fires (default 0.6)")
    args = ap.parse_args(argv)

    plaintext, glyphs = load_message()

    if args.preview or not args.schedule:
        print(f"plaintext : {plaintext}")
        print(f"length    : {len(glyphs)} glyphs")
        print(f"roundtrip : {decode(glyphs)}")
        ok = decode(glyphs).strip() == plaintext.strip()
        print(f"verify    : {'OK' if ok else 'MISMATCH — cipher is broken'}")
        print()
        for i, g in enumerate(glyphs):
            print(f"  {i:>3}  {g:>2}  {NIDANA[g]}")
        if not ok:
            return 1

    if args.schedule:
        need = len(glyphs)
        have = int(args.schedule * args.rate)
        print(f"\nover {args.schedule} episodes at a {args.rate:.0%} firing rate:")
        print(f"  firings available : ~{have}")
        print(f"  glyphs required   : {need}")
        if have >= need:
            print(f"  VERDICT: message completes with ~{have - need} firings to spare.")
        else:
            print(f"  VERDICT: SHORT BY ~{need - have}. Shorten the plaintext or raise "
                  f"the firing rate (lower glyph.single's min_confidence).")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
