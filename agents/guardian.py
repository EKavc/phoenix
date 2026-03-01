"""
Guardian — monitors system state
Measures: entropy + quality + delta quality
Signals: Chaos, Sol, (Limes is written by Alchemist)
"""

import math
from typing import List, Optional
from boards.blackboard import Blackboard, Entry, Tag


class Guardian:
    """Guardian — mathematical system monitor"""

    name = "Guardian"

    ENTROPY_DROP_THRESHOLD  = 0.15   # entropy drop > 15% triggers signal
    DELTA_QUALITY_THRESHOLD = 0.05   # delta quality < 5% = stagnation
    MIN_ROUNDS_BEFORE_CHAOS = 3      # minimum rounds before first Chaos
    QUALITY_RISING_FOR_SOL  = 0.10   # quality must rise > 10% for Sol

    def __init__(self, blackboard: Blackboard):
        self.bb = blackboard
        self.entropy_history: List[float] = []
        self.quality_history: List[float] = []
        self.chaos_called = False

    def compute_entropy(self) -> float:
        """Shannon entropy over tags on the ideas board. Normalized 0-1."""
        ideas = self.bb.ideas
        if len(ideas) < 3:
            return 1.0

        recent = ideas[-10:]
        tag_counts = {}
        for entry in recent:
            tag = entry.tag.value if entry.tag else "none"
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        total = len(recent)
        entropy = 0.0
        for count in tag_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        max_entropy = math.log2(len(tag_counts)) if len(tag_counts) > 1 else 1
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def compute_quality(self) -> float:
        """Ratio of Aurum entries in last 10 ideas."""
        recent = self.bb.ideas[-10:]
        if not recent:
            return 0.0
        aurum_count = sum(1 for e in recent if e.tag == Tag.AURUM)
        return aurum_count / len(recent)

    def evaluate(self) -> Optional[Tag]:
        """
        Main Guardian logic.
        Returns: Chaos, Sol, or None (continue)
        """
        round_num = self.bb.current_round

        if round_num < self.MIN_ROUNDS_BEFORE_CHAOS:
            return None

        entropy = self.compute_entropy()
        quality = self.compute_quality()

        self.entropy_history.append(entropy)
        self.quality_history.append(quality)

        print(f"\n  [{self.name}] Round {round_num}: entropy={entropy:.2f}, quality={quality:.2f}")

        if len(self.entropy_history) < 2:
            return None

        delta_quality = quality - self.quality_history[-2] if len(self.quality_history) >= 2 else 0
        entropy_drop  = self.entropy_history[-2] - entropy if len(self.entropy_history) >= 2 else 0

        print(f"  [{self.name}] delta_quality={delta_quality:.2f}, entropy_drop={entropy_drop:.2f}")

        # Sol: entropy drops AND quality rises → converging to solution
        if entropy_drop > self.ENTROPY_DROP_THRESHOLD and delta_quality > self.QUALITY_RISING_FOR_SOL:
            print(f"  [{self.name}] → SOL: system converging to solution")
            return Tag.SOL

        # Chaos: entropy drops AND quality stagnates → real stagnation
        if (entropy_drop > self.ENTROPY_DROP_THRESHOLD and
                abs(delta_quality) < self.DELTA_QUALITY_THRESHOLD):
            print(f"  [{self.name}] → CHAOS: stagnation detected")
            return Tag.CHAOS

        return None

    def call_chaos(self) -> Entry:
        """Write Chaos to system log"""
        entry = Entry(
            agent=self.name,
            content="Stagnation detected. Waking Alchemist.",
            tag=Tag.CHAOS
        )
        self.bb.log_system(entry)
        self.chaos_called = True
        return entry

    def call_sol(self) -> Entry:
        """Write Sol — system found a solution"""
        entry = Entry(
            agent=self.name,
            content="System converged. Solution exists. Shutting down.",
            tag=Tag.SOL
        )
        self.bb.log_system(entry)
        return entry
