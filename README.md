# 🔥 Phoenix

Experimental blackboard multi-agent architecture for solving complex problems.

Phoenix extends [Garden](../garden) with a meta-cognitive layer — the **Alchemist** —
which transforms failures into solutions and finds meta-patterns anywhere:
in science, music, biology.

---

## Architecture

```
Phoenix
├── Regular agents      — solve problem from their own angle, no overlap
├── Curator             — evaluates content (Aurum / Plumbum / Human)
├── Guardian            — monitors system state (entropy + quality + delta quality)
└── Alchemist           — meta-cognitive layer, finds meta-pattern, arxiv + brake
```

### Boards

| Board | Purpose |
|-------|---------|
| Ideas Board | Main working board |
| Error Board | Source of learning |
| Dead Branch | Source of inspiration |

### System Language

| Tag | Author | Meaning |
|-----|--------|---------|
| `Aurum` | Curator | Good idea |
| `Plumbum` | Curator | Bad idea / error |
| `Lux` | Alchemist | Found solution |
| `Chaos` | Guardian | Stagnation — wakes Alchemist |
| `Sol` | Guardian | System converged — exit |
| `Limes` | Alchemist | Beyond limits |
| `Human` | Curator | Human in the loop |

---

## Chaos Cycle

```
Guardian detects stagnation
    → Chaos
    → Alchemist: errors → dead branch → full board → arxiv
    → Alchemist: four-step self-reflection
        0. Shape  — what shape does the problem have?
        1. Raw    — what do I see?
        2. Mirror — what did I actually mean?
        3. Click  — meta-pattern
    → Alchemist: Brake — shape compatibility test
        PASS → Lux written to ideas board
        FAIL → goes to dead branch
    → Curator evaluates Lux
        → Aurum: system continues with new impulse
        → Plumbum: Alchemist tries again (max 3×)
        → Human: human decides
    → After 3× Plumbum: Limes
```

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/phoenix.git
cd phoenix
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env
```

## Run

```bash
python main.py
```

---

## Test Case

Design a system for sharing healthcare data between hospitals in Slovakia
while maintaining GDPR compliance and data sovereignty
(federated learning, differential privacy).

---

## Difference from Garden

| | Garden | Phoenix |
|---|---|---|
| Problem types | Configuration, design | Complex, research-level |
| Special agents | Curator | Curator + Guardian + Alchemist |
| Exit condition | Delta quality | Guardian (mathematical monitor) |
| External research | No | Yes (arxiv) |
| Human in the loop | No | Yes (Human) |
| Brake | No | Yes (shape compatibility) |
