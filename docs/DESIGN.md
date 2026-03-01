# Phoenix — Design Decisions

## Why non-overlapping roles?

Key insight from Garden: the system works well precisely because agents
have **no overlap** in their areas of concern. Each cuts the problem from a different angle.
This creates natural tension on the board that pushes the solution forward.

Agents cannot see each other — they communicate exclusively through the board.

## Why a mathematical Guardian?

The Guardian is not an intelligent agent — it is a mathematical monitor.
It measures three things: **entropy + quality + delta quality**.

- Entropy measures diversity of ideas on the board
- Quality = ratio of Aurum entries (Curator's evaluation)
- Delta quality = quality change between rounds

The combination distinguishes three states:
- Stagnation: entropy drops + delta quality ≈ 0 → **Chaos**
- Convergence: entropy drops + quality rises → **Sol**
- Gold-plating: entropy high + delta quality ≈ 0 → also **Sol**

Mathematical monitor instead of intelligent orchestrator:
simpler, more reliable, no hallucinations.

## Why does the Alchemist look for a meta-pattern?

Regular agents don't know what they don't know. When they hit a ceiling,
they circle the same solutions in different words.

The Alchemist doesn't read content — it reads the **pattern of failures**.
LLMs excel at recognizing abstract patterns across domains.
The meta-pattern is domain-independent — the same solution shape can
exist in music, biology, or architecture.

## Why four-step self-reflection?

The four steps mirror how insight actually works:
- Step 0 (Shape): zoom out, see the problem from above
- Step 1 (Raw): unfiltered first impression
- Step 2 (Mirror): treat your own output as a foreign text
- Step 3 (Click): the insight that emerges from the distance

Each step is a separate LLM call with a fresh context — the Mirror
genuinely sees the Raw output from outside, not as a continuation.

## Why the Brake?

Solutions have shapes. Problems have shapes.
Incompatible shapes cause more problems than they solve.
A solution that exports the problem elsewhere is not a solution.

The Brake tests shape compatibility before any Lux is written to the board.
It is not an ethical filter — it is a structural compatibility check.
If the shapes don't fit, harm may follow.

## Why Chaos only, no proactive Lux?

Proactive Lux (Guardian predicts stagnation before it happens)
was rejected as too complex. The Guardian would need to predict
the future from trends — unreliable and hard to tune.

Trade-off: the system sometimes waits unnecessarily for Chaos,
but it is cleaner. Verify empirically whether this matters.

## Why 3 attempts for the Alchemist?

A magic number. From fairy tales, mythology, alchemy.
The third attempt is always the decisive one. Verify empirically.
