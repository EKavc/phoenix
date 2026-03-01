"""
Phoenix Blackboard System
Boards: ideas, errors, dead_branch, system_log
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class Tag(str, Enum):
    AURUM   = "Aurum"    # good idea
    PLUMBUM = "Plumbum"  # bad idea / error
    LUX     = "Lux"      # Alchemist output
    CHAOS   = "Chaos"    # stagnation — wake Alchemist
    SOL     = "Sol"      # solution found, exit
    LIMES   = "Limes"    # beyond system limits
    HUMAN   = "Human"    # human in the loop


@dataclass
class Entry:
    agent: str
    content: str
    tag: Optional[Tag] = None
    ref: Optional[str] = None
    round_num: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

    def __str__(self):
        tag_str = f"[{self.tag.value}]" if self.tag else ""
        ref_str = f" →ref:{self.ref}" if self.ref else ""
        return f"[R{self.round_num}][{self.id}]{tag_str} {self.agent}: {self.content}{ref_str}"


class Blackboard:
    """Central blackboard — heart of Phoenix"""

    def __init__(self):
        self.ideas: List[Entry] = []
        self.errors: List[Entry] = []
        self.dead_branch: List[Entry] = []
        self.system_log: List[Entry] = []
        self.current_round = 0

    def add_idea(self, entry: Entry):
        entry.round_num = self.current_round
        self.ideas.append(entry)

    def add_error(self, entry: Entry):
        entry.round_num = self.current_round
        self.errors.append(entry)

    def add_to_dead_branch(self, entry: Entry):
        entry.round_num = self.current_round
        self.dead_branch.append(entry)

    def log_system(self, entry: Entry):
        entry.round_num = self.current_round
        self.system_log.append(entry)

    def get_ideas_by_round(self, round_num: int) -> List[Entry]:
        return [e for e in self.ideas if e.round_num == round_num]

    def get_aurum_ideas(self) -> List[Entry]:
        return [e for e in self.ideas if e.tag == Tag.AURUM]

    def get_lux_entries(self) -> List[Entry]:
        return [e for e in self.ideas if e.tag == Tag.LUX]

    def get_recent_ideas(self, n: int = 10) -> List[Entry]:
        return self.ideas[-n:]

    def next_round(self):
        self.current_round += 1

    def print_board(self):
        print("\n" + "="*60)
        print(f"IDEAS BOARD (round {self.current_round})")
        print("="*60)
        for e in self.ideas[-15:]:
            print(f"  {e}")

        if self.errors:
            print(f"\nERROR BOARD ({len(self.errors)} entries)")
            print("-"*40)
            for e in self.errors[-5:]:
                print(f"  {e}")

        if self.dead_branch:
            print(f"\nDEAD BRANCH ({len(self.dead_branch)} entries)")
            print("-"*40)
            for e in self.dead_branch[-5:]:
                print(f"  {e}")

        if self.system_log:
            print(f"\nSYSTEM")
            print("-"*40)
            for e in self.system_log[-3:]:
                print(f"  {e}")
        print("="*60 + "\n")
