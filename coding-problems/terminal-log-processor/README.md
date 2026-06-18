# Case Study: Universal Telematics Log Ingestion Pipeline

A simulation playground analyzing time-series event payloads from disparate, fragmented third-party hardware logs—inspired directly by universal API problems faced by logistics platforms like Terminal.

## The Core Challenges Targeted

1. **Polymorphic Payloads:** Normalizes incoming streams spanning completely differing key footprints (`t` vs `time`, `state` vs `status`) and localized provider status short-codes (`D` vs `DRIVING`).
2. **Fragile String Parsing:** Evaluates and cleanly translates inconsistent timestamp streams (ISO-8601, clean strings, stringified Epoch variants) into unified datetime objects natively.
3. **Chronological Fault Isolation:** Sorts out-of-order network data back into linear logical tracks without crashing execution strings when corrupt, invalid payloads drop down the wire.
4. **Compliance Checking:** Tracks rolling window logic constraints to calculate total aggregate vehicle movement profiles alongside safety thresholds (e.g., continuous driving durations exceeding 300 minutes without structured breaks).

## File Layout

* `mock_stream.json` — Raw, chaotic mock telemetry file featuring network drops and conflicting vendor formats.
* `solutions.py` — High-fault-tolerance data processing logic and calculations engine.

## How to Run It

Execute directly using a local Python terminal environment:

```bash
python solutions.py
```

## Explanation

1. Parsing (6 records → 5 valid, 1 dropped)
  - Index 3 ("CORRUPTED_PACKET_TEST") fails both ISO and strptime parsing → dropped ✓

2. Sort order after parsing:
  1) Index 1 — Unix ts 1771241400 → some date in early 2026 (before June), OFF_DUTY
  2) Index 0 — 2026-06-18 08:00:00, DRIVING
  3) Index 2 — 2026-06-18 12:05:00, DRIVING ("D" → normalized)
  4) Index 4 — 2026-06-18 13:35:00, DRIVING
  5) Index 5 — 2026-06-18 15:00:00, OFF_DUTY

3. Interval accumulation:

  | Interval | Status | Minutes | Cumulative Driving |
  |---|---|---|---|
  | Index1 → Index0 | OFF_DUTY | months | resets continuous to 0 |
  | 08:00 → 12:05 | DRIVING | 245 | 245 min |
  | 12:05 → 13:35 | DRIVING | 90 | 335 min → violation logged at 13:35 ✓ |
  | 13:35 → 15:00 | DRIVING | 85 | 420 min → violation logged at 15:00 ✓ |

  Total driving: 245 + 90 + 85 = 420 min ✓

  One thing to note: once a violation is flagged, continuous driving keeps accumulating (no reset), so the second violation at 15:00 shows 420 min rather than just the 85 min since the first flag. This is correct per the current logic — whether that's the intended behavior depends on the spec (some company rules re-flag per window, others accumulate). Worth a comment in the interview.
