# Phoenix

Experimental blackboard multi-agent architecture for solving complex, research-level problems.

Phoenix extends the blackboard pattern with a meta-cognitive layer — the **Alchemist** — which transforms failures into solutions by finding meta-patterns across science, music, biology, and other domains. A mathematical **Guardian** monitors system state and decides when to trigger the Alchemist or declare convergence.

> **Status:** Active research project.

---

## Architecture

```
Phoenix
+-- Regular agents      — solve problem from their own angle, no overlap
+-- Curator             — evaluates content (Aurum / Plumbum / Human)
+-- Guardian            — monitors system state (entropy + quality + delta quality)
+-- Alchemist           — meta-cognitive layer, finds meta-pattern, arxiv + brake
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
    -> Chaos
    -> Alchemist: errors -> dead branch -> full board -> arxiv
    -> Alchemist: four-step self-reflection
        0. Shape  — what shape does the problem have?
        1. Raw    — what do I see?
        2. Mirror — what did I actually mean?
        3. Click  — meta-pattern
    -> Alchemist: Brake — shape compatibility test
        PASS -> Lux written to ideas board
        FAIL -> goes to dead branch
    -> Curator evaluates Lux
        -> Aurum: system continues with new impulse
        -> Plumbum: Alchemist tries again (max 3x)
        -> Human: human decides
    -> After 3x Plumbum: Limes
```

---

## Installation

Requires Python 3.10+

```bash
git clone https://github.com/EKavc/phoenix.git
cd phoenix
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

## Usage

Select the active problem in `main.py`:

```python
ACTIVE = "healthcare"   # or "antibiotic", "scarring", "quantum"
```

Then run:

```bash
python main.py
# or
uv run main.py   # uv is a faster alternative to pip/python, see https://github.com/astral-sh/uv
```

Output is saved to `output_<problem>.txt`.

---

## Problems

Each problem has its own set of specialist agents defined in `problems.py`:

| Key | Problem | Agents |
|-----|---------|--------|
| `healthcare` | GDPR-compliant hospital data sharing in Slovakia | Lawyer, Architect, Security Expert, Clinician, Patient |
| `antibiotic` | Why does antibiotic resistance keep winning — and is there a way out? | Microbiologist, Infectious Disease Specialist, Epidemiologist, Evolutionary Biologist, Pharmacologist |
| `scarring` | Why do damaged complex systems scar instead of regenerate? | Structural Engineer, Distributed Systems Engineer, Economist, Thermodynamicist, Urban Planner |
| `wall` | How to detect when experts have hit the boundary of their collective domain | Epistemologist, Cognitive Scientist, Statistician |
| `quantum` | Why does measurement collapse quantum superposition — and what constitutes a measurement? | Quantum Field Theorist, Experimental Physicist, Quantum Information Theorist |
| `facts` | How to build an AI layer on HIS that guarantees patient data remains facts, never hallucinated | Epistemologist, Clinical Informaticist, AI Safety Architect, Auditor, Patient |
| `render` | How to render a verified fact tuple from HIS into a form an LLM can consume without hallucination | Database Engineer, Forensic Analyst, Auditor, Type System Designer, Epidemiologist |
| `role` | What role should an LLM play over HIS data — and what must it never do? | Air Traffic Controller, Anaesthesiologist, Judge, Medical Liability Lawyer, Cognitive Scientist |

To add a new problem, add a `ProblemConfig` entry to `problems.py` and select it via `ACTIVE` in `main.py`.

---

## Configuration

All tunable parameters are in `config.py`:

```python
MAIN_MODEL = "claude-opus-4-6"            # Alchemist
FAST_MODEL = "claude-haiku-4-5-20251001"  # Regular agents + Curator
MAX_ROUNDS = 20
ENTROPY_DROP_THRESHOLD = 0.10
# ... Guardian thresholds, Alchemist limits
```

---

## Project Structure

```
phoenix/
+-- agents/
|   +-- agents.py       — RegularAgent, Curator
|   +-- alchemist.py    — Alchemist (meta-cognitive layer)
|   +-- guardian.py     — Guardian (mathematical monitor)
+-- boards/
|   +-- blackboard.py   — Blackboard, Entry, Tag
+-- docs/
|   +-- DESIGN.md       — architecture notes
|   +-- LANGUAGE.md     — system language reference
+-- config.py           — all tunable parameters
+-- problems.py         — problem configs (problem + agents)
+-- phoenix.py          — main orchestrator
+-- main.py             — entry point, ACTIVE problem selector
+-- requirements.txt
+-- .env.example
```

---

## License

Research / experimental use. Contact the author for other uses.