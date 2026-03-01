"""
Alchemist — meta-cognitive layer of Phoenix

Four-step self-reflection process:
  0. Shape  — what shape does the problem have? (compass, zoom out)
  1. Raw    — what do I see?
  2. Mirror — what did I actually mean?
  3. Click  — meta-pattern

Then searches research (arxiv) and synthesizes Lux.
Brake: tests shape compatibility before writing Lux.
Chaos cycle: max 3 attempts, Aurum resets counter.
Tags: Lux (success), Limes (beyond limits)
"""

import requests
import xml.etree.ElementTree as ET
import anthropic
from boards.blackboard import Blackboard, Entry, Tag
from config import MAIN_MODEL


ARXIV_API = "http://export.arxiv.org/api/query"


def search_arxiv(query: str, max_results: int = 5) -> str:
    """Search arxiv for papers relevant to the meta-pattern"""
    try:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        response = requests.get(ARXIV_API, params=params, timeout=10)
        if response.status_code != 200:
            return "Arxiv unavailable."

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        results = []
        for entry in entries[:max_results]:
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            if title is not None and summary is not None:
                results.append(
                    f"PAPER: {title.text.strip()}\n"
                    f"ABSTRACT: {summary.text.strip()[:300]}..."
                )

        return "\n\n".join(results) if results else "No relevant papers found."
    except Exception as e:
        return f"Arxiv search error: {e}"


class Alchemist:
    """Alchemist — transforms Plumbum into Aurum"""

    name = "Alchemist"
    MAX_ATTEMPTS = 3

    def __init__(self, blackboard: Blackboard, client: anthropic.Anthropic, problem: str):
        self.bb = blackboard
        self.client = client
        self.problem = problem
        self.attempt_count = 0
        self.curator_feedback = []

    def reset_attempts(self):
        """Aurum from Curator resets the counter"""
        self.attempt_count = 0

    def _format_board_content(self, entries, label: str) -> str:
        if not entries:
            return f"{label}: empty\n"
        content = f"{label}:\n"
        for e in entries[-10:]:
            content += f"  - [{e.tag.value if e.tag else '?'}] {e.agent}: {e.content}\n"
        return content

    def _build_context(self, stage: int) -> str:
        """Builds context for Alchemist based on search stage"""
        context = f"PROBLEM: {self.problem}\n\n"
        context += f"ATTEMPT: {self.attempt_count}/{self.MAX_ATTEMPTS}\n\n"

        if self.curator_feedback:
            context += "CURATOR FEEDBACK:\n"
            for fb in self.curator_feedback[-3:]:
                context += f"  - {fb}\n"
            context += "\n"

        context += self._format_board_content(self.bb.errors, "ERROR BOARD")

        if stage >= 2:
            context += self._format_board_content(self.bb.dead_branch, "DEAD BRANCH")

        if stage >= 3:
            context += self._format_board_content(self.bb.ideas, "IDEAS BOARD (full)")

        return context

    # ── Four-step self-reflection ──────────────────────────────────────────────

    def _detect_shape(self, context: str) -> str:
        """
        Step 0 — Zoom out. What shape does the problem have?
        Shape is the compass — it directs the entire reflection.
        """
        print(f"  [{self.name}] Reflection 0/3: problem shape...")
        r0 = self.client.messages.create(
            model=MAIN_MODEL,
            max_tokens=200,
            system="""You are the Alchemist. Look at the problem and its failures from above.
Do not determine a solution. Determine the SHAPE of the problem.

Shape types:
- Linear: sequential steps, clear dependencies
- Layered: infrastructure must precede higher layers
- Network: everything connects, changing one changes others
- Antagonistic: two forces in tension, solution is balance not victory
- Open: problem boundaries are unclear

Format:
Shape: [type]
Implication: [what this means for how to solve it — 1 sentence]""",
            messages=[{"role": "user", "content": context}]
        )
        shape = r0.content[0].text
        print(f"  [{self.name}] Shape: {shape[:80]}...")
        return shape

    def _find_meta_pattern(self, context: str) -> tuple[str, str]:
        """
        Four-step self-reflection:
        0. Shape  — zoom out, compass
        1. Raw    — what do I see?
        2. Mirror — what did I actually mean?
        3. Click  — meta-pattern formulation
        """

        # ── Step 0: Shape ─────────────────────────────────────────────────────
        shape = self._detect_shape(context)
        context_enriched = f"{context}\n\nPROBLEM SHAPE:\n{shape}"

        # ── Step 1: Raw observation ───────────────────────────────────────────
        print(f"  [{self.name}] Reflection 1/3: what do I see...")
        r1 = self.client.messages.create(
            model=MAIN_MODEL,
            max_tokens=300,
            system="""You are the Alchemist. You are looking at system failures.
Write what you see — raw, unfiltered, without trying to solve anything.
Just describe the pattern you sense. 2-3 sentences.""",
            messages=[{"role": "user", "content": context_enriched}]
        )
        raw_observation = r1.content[0].text
        print(f"  [{self.name}] Raw: {raw_observation[:80]}...")

        # ── Step 2: Mirror ────────────────────────────────────────────────────
        print(f"  [{self.name}] Reflection 2/3: what did I mean...")
        r2 = self.client.messages.create(
            model=MAIN_MODEL,
            max_tokens=300,
            system="""You are the Alchemist. Someone showed you your own observation.
Read it as if it were written by someone else. What is behind it? What is the author actually saying?
What deeper pattern hides there? Could it relate to something from another domain?
2-3 sentences.""",
            messages=[{"role": "user", "content": f"MY OBSERVATION:\n{raw_observation}"}]
        )
        deeper = r2.content[0].text
        print(f"  [{self.name}] Deeper: {deeper[:80]}...")

        # ── Step 3: Click ─────────────────────────────────────────────────────
        print(f"  [{self.name}] Reflection 3/3: click...")
        r3 = self.client.messages.create(
            model=MAIN_MODEL,
            max_tokens=400,
            system="""You are the Alchemist. You have the problem shape, raw observation, and deeper reflection.
Now formulate the META-PATTERN — an abstract pattern behind the concrete failures.
The pattern may come from another domain: music, biology, physics, architecture.
Format:
Meta-pattern: [1-2 sentences]
Research keywords: [3-5 words for arxiv]""",
            messages=[{"role": "user", "content":
                f"PROBLEM SHAPE:\n{shape}\n\n"
                f"RAW OBSERVATION:\n{raw_observation}\n\n"
                f"DEEPER REFLECTION:\n{deeper}"}]
        )
        meta_pattern = r3.content[0].text
        return meta_pattern, shape

    def _synthesize_solution(self, meta_pattern: str, research: str) -> str:
        """Synthesizes solution from meta-pattern and research"""
        prompt = f"""META-PATTERN: {meta_pattern}

ARXIV RESEARCH:
{research}

Based on the meta-pattern and research, propose a CONCRETE solution or new angle.
The solution must be applicable to: {self.problem}
It may come from another domain (music, biology, architecture) — that is fine.
Be specific and concise (max 3-4 sentences)."""

        response = self.client.messages.create(
            model=MAIN_MODEL,
            max_tokens=400,
            system="You are the Alchemist. You transform knowledge from other domains into solutions.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _validate_solution(self, solution: str, problem_shape: str) -> tuple[bool, str]:
        """
        Brake — shape compatibility test.

        A solution has a shape. A problem has a shape.
        If incompatible → solution causes more problems.
        If solution exports the problem elsewhere → it is not a solution.

        Returns: (is_valid, reason)
        """
        print(f"  [{self.name}] Brake: testing shape compatibility...")
        response = self.client.messages.create(
            model=MAIN_MODEL,
            max_tokens=300,
            system="""You are the Alchemist. You have a proposed solution and the problem shape.
Your role is the BRAKE — test whether the solution causes more harm than good.

Check:
1. Solution shape: what shape does this solution have?
2. Compatibility: is the solution shape compatible with the problem shape?
3. Export: does the solution export the problem elsewhere? (to other people, to the future, to another system)
4. Side effects: what undesired consequences could it have?

Response format:
Solution shape: [type]
Compatible: Yes/No
Problem export: Yes/No — [where]
Verdict: PASS / FAIL
Reason: [1-2 sentences]""",
            messages=[{"role": "user", "content":
                f"PROBLEM SHAPE:\n{problem_shape}\n\n"
                f"PROPOSED SOLUTION:\n{solution}"}]
        )
        text = response.content[0].text
        print(f"  [{self.name}] Brake: {text[:100]}...")

        is_valid = "Verdict: PASS" in text
        reason = ""
        if "Reason:" in text:
            reason = text.split("Reason:")[-1].strip()

        if not is_valid:
            print(f"  [{self.name}] ⚠ Brake FAIL: {reason[:80]}")
        else:
            print(f"  [{self.name}] ✓ Brake PASS")

        return is_valid, reason

    def _extract_keywords(self, meta_pattern: str) -> str:
        """Extracts arxiv search keywords from meta-pattern"""
        if "Research keywords:" in meta_pattern:
            keywords = meta_pattern.split("Research keywords:")[-1].strip()
            return keywords[:100]
        return meta_pattern[:50]

    def attempt(self) -> Entry:
        """One Alchemist attempt — returns Lux entry"""
        self.attempt_count += 1
        print(f"\n  [{self.name}] Attempt {self.attempt_count}/{self.MAX_ATTEMPTS}")

        stage = self.attempt_count

        # 1. Self-reflection (0→1→2→3)
        context = self._build_context(stage)
        meta_pattern, problem_shape = self._find_meta_pattern(context)
        print(f"  [{self.name}] Meta-pattern: {meta_pattern[:100]}...")

        # 2. Arxiv
        keywords = self._extract_keywords(meta_pattern)
        print(f"  [{self.name}] Searching arxiv: {keywords}")
        research = search_arxiv(keywords)

        # 3. Synthesis
        solution = self._synthesize_solution(meta_pattern, research)
        print(f"  [{self.name}] Solution: {solution[:100]}...")

        # 4. Brake — shape compatibility test
        is_valid, brake_reason = self._validate_solution(solution, problem_shape)

        if not is_valid:
            # Failed brake — goes to dead branch, not ideas board
            self.bb.add_to_dead_branch(Entry(
                agent=self.name,
                content=f"[BRAKE FAIL] {solution[:150]} | Reason: {brake_reason}",
                tag=Tag.PLUMBUM
            ))
            print(f"  [{self.name}] Solution redirected to dead branch.")
            entry = Entry(
                agent=self.name,
                content=f"[BRAKE FAIL — see dead branch] {brake_reason}",
                tag=Tag.LUX
            )
            self.bb.add_idea(entry)
            return entry

        # 5. Write Lux — solution passed brake
        content = f"[SHAPE+META-PATTERN: {meta_pattern[:100]}...] SOLUTION: {solution}"
        entry = Entry(agent=self.name, content=content, tag=Tag.LUX)
        self.bb.add_idea(entry)
        print(f"  [{self.name}] Lux written: {entry.id}")
        return entry

    def write_limes(self) -> Entry:
        """Alchemist exhausted all attempts — Limes"""
        entry = Entry(
            agent=self.name,
            content=f"Exhausted {self.MAX_ATTEMPTS} attempts. "
                    f"Problem exceeds system capabilities. "
                    f"Recommendation: change the problem statement or try a stronger model.",
            tag=Tag.LIMES
        )
        self.bb.log_system(entry)
        print(f"\n  [{self.name}] LIMES — beyond limits")
        return entry

    def receive_curator_feedback(self, feedback: str):
        """Receives feedback from Curator"""
        self.curator_feedback.append(feedback)
