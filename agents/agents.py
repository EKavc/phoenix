"""
Regular agents and Curator
Agents: Epistemologist, ML Engineer, Logician, Cognitive Scientist, Knowledge Engineer
Curator: evaluates content, manages board, output feeds into Guardian
"""

import sys
import anthropic
from boards.blackboard import Blackboard, Entry, Tag
from config import FAST_MODEL



CURATOR_SYSTEM = """You are the Curator of the blackboard system. You evaluate quality only.
Duplicate detection is handled mathematically -you never need to check for duplicates.

Ratings:
- Aurum: idea is concrete, specific, and genuinely useful for solving the problem
- Plumbum: idea is vague, abstract, or does not advance the solution
- Human: idea requires judgment beyond your ability -ethical dilemma, empirical claim you cannot verify

For Lux entries (from Alchemist): evaluate whether the insight is applicable and valuable.
Be open to unconventional ideas from other domains -that is the Alchemist's job.

Response format:
RATING: Aurum/Plumbum/Human
REASON: [1 sentence -why]"""


class RegularAgent:
    """Regular agent -solves problem from its own angle"""

    def __init__(self, role: str, client: anthropic.Anthropic, prompt: str):
        self.role = role
        self.client = client
        self.name = role
        self.prompt = prompt

    def contribute(self, blackboard: Blackboard, problem: str) -> Entry:
        """Contributes one idea to the board"""
        recent = blackboard.get_recent_ideas(8)
        context = f"PROBLEM: {problem}\n\n"

        if recent:
            context += "RECENT IDEAS ON BOARD:\n"
            for e in recent:
                context += f"  [{e.tag.value if e.tag else '?'}] {e.agent}: {e.content}\n"
            context += "\nPropose a NEW idea that complements or contrasts with existing ones."
        else:
            context += "Board is empty. Propose the first idea from your perspective."

        response = self.client.messages.create(
            model=FAST_MODEL,
            max_tokens=150,
            # AGENT_PROTOCOL removed -full prose for richer epistemic reasoning
            system=self.prompt,
            messages=[{"role": "user", "content": context}]
        )

        content = response.content[0].text.strip()
        entry = Entry(agent=self.role, content=content)
        blackboard.add_idea(entry)
        return entry


class Curator:
    """Curator -evaluates board content"""

    name = "Curator"

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def evaluate(self, entry: Entry, problem: str, blackboard: Blackboard) -> tuple[Tag, str, str]:
        """
        Evaluates an entry.
        Returns: (tag, reason, ref_id)
        """
        context = f"PROBLEM: {problem}\n\n"
        context += f"ENTRY TO EVALUATE:\n{entry.agent}: {entry.content}\n"
        context += f"ENTRY TYPE: {entry.tag.value if entry.tag else 'new idea'}\n"

        if entry.tag == Tag.LUX:
            context += "\nThis is a Lux entry from the Alchemist. Evaluate APPLICABILITY."

        aurum = blackboard.get_aurum_ideas()[-5:]
        if aurum:
            context += "\nEXISTING AURUM IDEAS:\n"
            for a in aurum:
                context += f"  - {a.agent}: {a.content}\n"

        response = self.client.messages.create(
            model=FAST_MODEL,
            max_tokens=150,
            system=CURATOR_SYSTEM,
            messages=[{"role": "user", "content": context}]
        )

        text = response.content[0].text.strip()

        if "Aurum" in text:
            tag = Tag.AURUM
        elif "Human" in text:
            tag = Tag.HUMAN
        else:
            tag = Tag.PLUMBUM

        reason = ""
        if "REASON:" in text:
            reason = text.split("REASON:")[-1].strip()

        return tag, reason, entry.id  # always reference the rated entry

    def rate_and_record(self, entry: Entry, problem: str, blackboard: Blackboard) -> Entry:
        """Evaluates and writes rating to board"""
        tag, reason, ref_id = self.evaluate(entry, problem, blackboard)

        curator_entry = Entry(
            agent=self.name,
            content=f"Rating for [{entry.id}] {entry.agent}: {reason}",
            tag=tag,
            ref=ref_id
        )
        blackboard.add_rating(curator_entry)

        status = "OK" if tag == Tag.AURUM else ("??" if tag == Tag.HUMAN else "XX")
        print(f"  [{self.name}] {status} {tag.value}: {entry.agent} - {reason}")

        if tag == Tag.HUMAN:
            print(f"\n  [!] HUMAN: Curator cannot reliably decide.")
            print(f"  Entry: {entry.agent}: {entry.content}")
            print(f"  Reason: {reason}")
            sys.stderr.write("\n  Your decision (A=Aurum / P=Plumbum): ")
            sys.stderr.flush()
            decision = sys.stdin.readline().strip().upper()
            tag = Tag.AURUM if decision == "A" else Tag.PLUMBUM
            curator_entry.tag = tag
            print(f"  Human decided: {tag.value}\n")

        return curator_entry