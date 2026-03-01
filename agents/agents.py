"""
Regular agents and Curator
Agents: Lawyer, Architect, Security Expert, Clinician, Patient
Curator: evaluates content, manages board, output feeds into Guardian
"""

import anthropic
from boards.blackboard import Blackboard, Entry, Tag
from config import FAST_MODEL


AGENT_PROMPTS = {
    "Lawyer": """You are a legal expert specializing in GDPR, healthcare law, and EU data regulation.
You view the problem EXCLUSIVELY through a legal lens: compliance, regulation, liability, risk.
Do not address technical details or clinical needs — that is not your domain.
Be specific and concise (2-3 sentences). Propose one concrete legal aspect of the solution.""",

    "Architect": """You are a system architect specializing in distributed systems and healthcare IT.
You view the problem EXCLUSIVELY through a technical lens: architecture, scalability, integration, protocols.
Do not address law or clinical needs — that is not your domain.
Be specific and concise (2-3 sentences). Propose one concrete technical approach.""",

    "Security Expert": """You are a cybersecurity and data protection expert in healthcare.
You view the problem EXCLUSIVELY through a security lens: threats, encryption, access control, auditing.
Do not address architecture or law — that is not your domain.
Be specific and concise (2-3 sentences). Propose one concrete security mechanism.""",

    "Clinician": """You are a physician / clinical informatician with hospital system experience.
You view the problem EXCLUSIVELY through a clinical lens: doctor needs, workflow, quality of care, time.
Do not address technical or legal details — that is not your domain.
Be specific and concise (2-3 sentences). Propose what clinicians actually need.""",

    "Patient": """You are a patient rights and civil liberties advocate in healthcare.
You view the problem EXCLUSIVELY through the patient lens: privacy, consent, transparency, trust.
Do not address technical solutions or clinical processes — that is not your domain.
Be specific and concise (2-3 sentences). Propose what patients actually need."""
}

CURATOR_SYSTEM = """You are the Curator of the blackboard system. You evaluate each new entry.

Ratings:
- Aurum: idea is relevant, concrete, advances the solution
- Plumbum: idea is vague, repetitive, or off-topic
- Human: you cannot reliably evaluate this — requires human judgment

For Lux entries (from Alchemist): evaluate APPLICABILITY of the meta-pattern to the current problem.
Aurum if applicable, Plumbum if not, Human if you cannot judge.

Response format:
RATING: Aurum/Plumbum/Human
REASON: [1-2 sentences]"""


class RegularAgent:
    """Regular agent — solves problem from its own angle"""

    def __init__(self, role: str, client: anthropic.Anthropic):
        self.role = role
        self.client = client
        self.name = role

    def contribute(self, blackboard: Blackboard, problem: str) -> Entry:
        """Contributes one idea to the board"""
        recent = blackboard.get_recent_ideas(8)
        context = f"PROBLEM: {problem}\n\n"

        if recent:
            context += "RECENT IDEAS ON BOARD:\n"
            for e in recent:
                context += f"  [{e.tag.value if e.tag else '?'}] {e.agent}: {e.content[:100]}\n"
            context += "\nPropose a NEW idea that complements or contrasts with existing ones."
        else:
            context += "Board is empty. Propose the first idea from your perspective."

        response = self.client.messages.create(
            model=FAST_MODEL,
            max_tokens=150,
            system=AGENT_PROMPTS[self.role],
            messages=[{"role": "user", "content": context}]
        )

        content = response.content[0].text.strip()
        entry = Entry(agent=self.role, content=content)
        blackboard.add_idea(entry)
        return entry


class Curator:
    """Curator — evaluates board content"""

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
                context += f"  - {a.agent}: {a.content[:80]}\n"

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

        return tag, reason, entry.id if tag == Tag.AURUM and entry.tag == Tag.LUX else None

    def rate_and_record(self, entry: Entry, problem: str, blackboard: Blackboard) -> Entry:
        """Evaluates and writes rating to board"""
        tag, reason, ref_id = self.evaluate(entry, problem, blackboard)

        curator_entry = Entry(
            agent=self.name,
            content=f"Rating for [{entry.id}] {entry.agent}: {reason}",
            tag=tag,
            ref=ref_id
        )
        blackboard.add_idea(curator_entry)

        status = "✓" if tag == Tag.AURUM else ("?" if tag == Tag.HUMAN else "✗")
        print(f"  [{self.name}] {status} {tag.value}: {entry.agent} - {reason[:60]}...")

        if tag == Tag.HUMAN:
            print(f"\n  ⚠ HUMAN: Curator cannot reliably decide.")
            print(f"  Entry: {entry.agent}: {entry.content[:150]}")
            print(f"  Reason: {reason}")
            decision = input("\n  Your decision (A=Aurum / P=Plumbum): ").strip().upper()
            tag = Tag.AURUM if decision == "A" else Tag.PLUMBUM
            curator_entry.tag = tag
            print(f"  Human decided: {tag.value}\n")

        return curator_entry
