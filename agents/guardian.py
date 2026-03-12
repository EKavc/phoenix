"""
Guardian — monitors system state
Measures ONLY agent ideas — not curator ratings.
Signals: Chaos, Sol
"""

import math
from typing import List, Optional
from boards.blackboard import Blackboard, Entry, Tag
import config


class Guardian:
    """Guardian - mathematical system monitor"""

    name = "Guardian"

    ENTROPY_DROP_THRESHOLD    = config.ENTROPY_DROP_THRESHOLD
    DELTA_QUALITY_THRESHOLD   = config.DELTA_QUALITY_THRESHOLD
    MIN_ROUNDS_BEFORE_CHAOS   = config.MIN_ROUNDS_BEFORE_CHAOS
    QUALITY_RISING_FOR_SOL    = config.QUALITY_RISING_FOR_SOL
    QUALITY_SUSTAINED_FOR_SOL = config.QUALITY_SUSTAINED_FOR_SOL
    GOLD_PLATING_MAX_QUALITY  = config.GOLD_PLATING_MAX_QUALITY
    WALL_QUALITY_CEILING      = config.WALL_QUALITY_CEILING
    WALL_DIVERSITY_FLOOR      = config.WALL_DIVERSITY_FLOOR
    WALL_ROUNDS               = config.WALL_ROUNDS

    def __init__(self, blackboard: Blackboard):
        self.bb = blackboard
        self.entropy_history: List[float] = []
        self.quality_history: List[float] = []
        self.plumbum_history: List[float] = []

    def compute_entropy(self) -> float:
        """
        Semantic diversity of recent agent ideas.
        Measures content similarity — not tag distribution.
        Approximation: unique word overlap across last N ideas.
        """
        ideas = self.bb.ideas[-10:]  # agent ideas only
        if len(ideas) < 3:
            return 1.0

        # Split each idea into word sets
        word_sets = [set(e.content.lower().split()) for e in ideas]

        # Average pairwise Jaccard distance (1 = totally different, 0 = identical)
        distances = []
        for i in range(len(word_sets)):
            for j in range(i + 1, len(word_sets)):
                a, b = word_sets[i], word_sets[j]
                union = len(a | b)
                if union == 0:
                    distances.append(0.0)
                else:
                    jaccard_sim = len(a & b) / union
                    distances.append(1 - jaccard_sim)  # distance

        if not distances:
            return 1.0

        # Average distance = entropy proxy. High = diverse, Low = repetitive
        avg_distance = sum(distances) / len(distances)
        return avg_distance

    def compute_quality(self) -> float:
        """
        Ratio of agent ideas rated Aurum by Curator in last 10 ideas.
        Uses ratings board — not idea tags.
        """
        recent_ideas = self.bb.ideas[-10:]
        if not recent_ideas:
            return 0.0

        aurum_count = sum(
            1 for e in recent_ideas
            if self.bb.get_rating_for(e.id) == Tag.AURUM
        )
        return aurum_count / len(recent_ideas)

    def compute_plumbum(self) -> float:
        """
        Ratio of agent ideas rated Plumbum by Curator in last 10 ideas.
        High plumbum + high diversity = agents hitting a wall.
        """
        recent_ideas = self.bb.ideas[-10:]
        if not recent_ideas:
            return 0.0
        plumbum_count = sum(
            1 for e in recent_ideas
            if self.bb.get_rating_for(e.id) == Tag.PLUMBUM
        )
        return plumbum_count / len(recent_ideas)

    def is_duplicate(self, entry: "Entry", threshold: float = 0.35) -> tuple[bool, str]:
        """
        Mathematical duplicate detection via Jaccard similarity.
        Compares new entry against all existing Aurum ideas.
        Returns: (is_duplicate, reason)
        """
        stop_words = {"the", "a", "an", "is", "are", "with", "and", "or", "for",
                      "to", "of", "in", "that", "this", "each", "all", "any",
                      "by", "as", "at", "be", "it", "its", "not", "on", "per",
                      "we", "our", "which", "will", "must", "should", "can", "has"}
        new_words = set(entry.content.lower().split()) - stop_words
        if not new_words:
            return False, ""

        aurum_ideas = self.bb.get_rated_ideas()
        if not aurum_ideas:
            return False, ""

        for aurum in aurum_ideas:
            aurum_words = set(aurum.content.lower().split()) - stop_words
            union = len(new_words | aurum_words)
            if union == 0:
                continue
            similarity = len(new_words & aurum_words) / union
            if similarity >= threshold:
                return True, f"Jaccard={similarity:.2f} vs [{aurum.id}] {aurum.agent}"

        return False, ""

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
        plumbum = self.compute_plumbum()

        self.entropy_history.append(entropy)
        self.quality_history.append(quality)
        self.plumbum_history.append(plumbum)

        print(f"\n  [{self.name}] Round {round_num}: diversity={entropy:.2f}, quality={quality:.2f}, plumbum={plumbum:.2f}")

        if len(self.entropy_history) < 2:
            return None

        delta_quality = quality - self.quality_history[-2]
        entropy_drop  = self.entropy_history[-2] - entropy

        print(f"  [{self.name}] delta_quality={delta_quality:+.2f}, diversity_drop={entropy_drop:+.2f}")

        # Sol: diversity drops AND quality rises → converging to good solution
        if entropy_drop > self.ENTROPY_DROP_THRESHOLD and delta_quality > self.QUALITY_RISING_FOR_SOL:
            print(f"  [{self.name}] -> SOL: converging to solution")
            return Tag.SOL

        # Sol: sustained high quality for 4+ rounds → system found a stable solution
        # NOTE: checked BEFORE gold-plating — high flat quality is SOL, not CHAOS
        if len(self.quality_history) >= 4:
            recent_q = self.quality_history[-4:]
            if min(recent_q) > self.QUALITY_SUSTAINED_FOR_SOL:
                print(f"  [{self.name}] -> SOL: sustained quality ({min(recent_q):.2f}+ for 4 rounds)")
                return Tag.SOL

        # Chaos: diversity drops AND quality stagnates → repetition without progress
        if (entropy_drop > self.ENTROPY_DROP_THRESHOLD and
                abs(delta_quality) < self.DELTA_QUALITY_THRESHOLD):
            print(f"  [{self.name}] -> CHAOS: stagnation detected")
            return Tag.CHAOS

        # Gold-plating: quality flat AND low → varied but redundant content
        # High flat quality is SOL (checked above), not gold-plating
        if len(self.quality_history) >= 4:
            recent_q = self.quality_history[-4:]
            q_range = max(recent_q) - min(recent_q)
            if q_range < self.DELTA_QUALITY_THRESHOLD and recent_q[-1] < self.GOLD_PLATING_MAX_QUALITY:
                print(f"  [{self.name}] -> CHAOS: gold-plating detected (quality flat={recent_q[-1]:.2f} for 4 rounds)")
                return Tag.CHAOS

        # Wall detection: agents diverse but Curator keeps rejecting
        # avg quality low + avg diversity high = problem is outside their domain
        # Use average so one good round doesn't mask sustained failure
        if len(self.quality_history) >= self.WALL_ROUNDS:
            recent_q = self.quality_history[-self.WALL_ROUNDS:]
            recent_e = self.entropy_history[-self.WALL_ROUNDS:]
            avg_q = sum(recent_q) / len(recent_q)
            avg_e = sum(recent_e) / len(recent_e)
            if avg_q < self.WALL_QUALITY_CEILING and avg_e > self.WALL_DIVERSITY_FLOOR:
                print(f"  [{self.name}] -> CHAOS: wall detected "
                      f"(avg quality={avg_q:.2f}<{self.WALL_QUALITY_CEILING}, "
                      f"avg diversity={avg_e:.2f}>{self.WALL_DIVERSITY_FLOOR} "
                      f"for {self.WALL_ROUNDS} rounds)")
                return Tag.CHAOS

        return None

    def call_chaos(self) -> Entry:
        entry = Entry(
            agent=self.name,
            content="Stagnation detected. Waking Alchemist.",
            tag=Tag.CHAOS
        )
        self.bb.log_system(entry)
        return entry

    def call_sol(self) -> Entry:
        entry = Entry(
            agent=self.name,
            content="System converged. Solution exists. Shutting down.",
            tag=Tag.SOL
        )
        self.bb.log_system(entry)
        return entry