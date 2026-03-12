"""
Phoenix — main orchestrator
Manages normal flow, calls Guardian, Alchemist, Curator
"""

import anthropic
from boards.blackboard import Blackboard, Entry, Tag
from agents.guardian import Guardian
from agents.alchemist import Alchemist
from agents.agents import RegularAgent, Curator


class Phoenix:
    """Phoenix architecture - blackboard system with Alchemist"""

    MAX_ROUNDS = 20

    def __init__(self, config, api_key: str = None):
        self.problem = config.problem.strip()
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.bb = Blackboard()

        self.agents = [
            RegularAgent(role, self.client, prompt)
            for role, prompt in config.agents.items()
        ]
        self.curator  = Curator(self.client)
        self.guardian = Guardian(self.bb)
        self.alchemist = Alchemist(self.bb, self.client, self.problem)

        self.state = "running"
        self.chaos_failures = 0  # consecutive failed Chaos cycles
        self.MAX_CHAOS_FAILURES = 3  # Limes after this many failures

    def _run_normal_round(self):
        """Normal round — agents contribute, Curator evaluates"""
        print(f"\n{'-'*50}")
        print(f"ROUND {self.bb.current_round} — Normal flow")
        print(f"{'-'*50}")

        new_entries = []
        for agent in self.agents:
            entry = agent.contribute(self.bb, self.problem)
            print(f"  [{agent.name}]: {entry.content}")
            new_entries.append(entry)

        print(f"\n  Curator evaluating...")
        for entry in new_entries:
            is_dup, dup_reason = self.guardian.is_duplicate(entry)
            if is_dup:
                # Mathematical duplicate — skip Curator, record Plumbum directly
                from boards.blackboard import Entry as E
                dup_entry = E(
                    agent=self.curator.name,
                    content=f"Duplicate [{entry.id}] {entry.agent}: {dup_reason}",
                    tag=Tag.PLUMBUM,
                    ref=entry.id
                )
                self.bb.add_rating(dup_entry)
                print(f"  [Guardian] DUP {entry.agent}: {dup_reason}")
            else:
                self.curator.rate_and_record(entry, self.problem, self.bb)

    def _run_chaos_cycle(self) -> bool:
        """
        Chaos cycle — Alchemist tries to unblock the system.
        Returns True if success (Aurum), False if Limes.
        """
        print(f"\n{'='*50}")
        print(f"CHAOS — Alchemist waking up")
        print(f"{'='*50}")

        self.guardian.call_chaos()

        while self.alchemist.attempt_count < self.alchemist.MAX_ATTEMPTS:
            lux_entry = self.alchemist.attempt()

            # Skip Curator for BRAKE FAIL entries — they go straight to dead branch
            if "[BRAKE FAIL" in lux_entry.content:
                print(f"  [Alchemist] BRAKE FAIL — skipping Curator, going to dead branch.")
                self.bb.ideas.remove(lux_entry)  # remove from ideas
                self.bb.add_to_dead_branch(Entry(
                    agent=self.alchemist.name,
                    content=f"Brake fail: {lux_entry.content}",
                    tag=Tag.PLUMBUM
                ))
                self.alchemist.receive_curator_feedback("Brake failed — solution incompatible with problem shape.")
                continue

            print(f"\n  [Curator] Evaluating Lux...")
            curator_entry = self.curator.rate_and_record(lux_entry, self.problem, self.bb)

            if curator_entry.tag == Tag.AURUM:
                print(f"\n  [OK] Curator accepted Lux as Aurum!")
                print(f"  Guardian: Waking regular agents with new impulse.")
                self.alchemist.reset_attempts()
                self.state = "running"
                return True
            else:
                feedback = curator_entry.content
                self.alchemist.receive_curator_feedback(feedback)
                print(f"\n  [XX] Curator rejected Lux. Alchemist tries again...")

                # Move rejected Lux to dead branch
                self.bb.add_to_dead_branch(Entry(
                    agent=self.alchemist.name,
                    content=f"Rejected Lux: {lux_entry.content}",
                    tag=Tag.PLUMBUM
                ))

        self.alchemist.write_limes()
        self.state = "limes"
        return False

    def run(self) -> dict:
        """Main Phoenix loop"""
        print(f"\n{'#'*60}")
        print(f"PHOENIX START")
        print(f"PROBLEM: {self.problem}")
        print(f"{'#'*60}\n")

        result = {
            "status": None,
            "rounds": 0,
            "final_ideas": [],
            "chaos_triggered": False
        }

        while self.bb.current_round < self.MAX_ROUNDS:
            self.bb.next_round()

            if self.state == "running":
                self._run_normal_round()

            guardian_signal = self.guardian.evaluate()

            if guardian_signal == Tag.SOL:
                self.guardian.call_sol()
                self.state = "sol"
                break

            elif guardian_signal == Tag.CHAOS:
                result["chaos_triggered"] = True
                success = self._run_chaos_cycle()
                if not success:
                    if self.state == "limes":
                        # Alchemist exhausted all attempts — immediate exit
                        print(f"\n  [Phoenix] Alchemist reached Limes. Stopping.")
                        break
                    # Chaos failed but no Limes yet — count and maybe retry
                    self.chaos_failures += 1
                    if self.chaos_failures >= self.MAX_CHAOS_FAILURES:
                        print(f"\n  [Phoenix] {self.MAX_CHAOS_FAILURES}x Chaos failed. Limes.")
                        self.state = "limes"
                        break
                    else:
                        self.alchemist.attempt_count = 0
                        self.state = "running"
                else:
                    self.chaos_failures = 0  # success resets the counter

            if self.bb.current_round % 3 == 0:
                self.bb.print_board()

        self.bb.print_board()
        result["rounds"] = self.bb.current_round
        result["status"] = self.state
        result["final_ideas"] = [str(e) for e in self.bb.get_aurum_ideas()[-5:]]

        self._print_summary(result)
        return result

    def _print_summary(self, result: dict):
        print(f"\n{'#'*60}")
        print(f"PHOENIX SUMMARY")
        print(f"{'#'*60}")
        print(f"Status: {result['status'].upper()}")
        print(f"Rounds: {result['rounds']}")
        print(f"Chaos: {'Yes' if result['chaos_triggered'] else 'No'}")
        print(f"\nTop ideas (Aurum):")
        for idea in result["final_ideas"]:
            print(f"  {idea}")

        if result["status"] == "sol":
            print(f"\n[OK] SOL: System found a solution.")
        elif result["status"] == "limes":
            print(f"\n[!!] LIMES: Change the problem statement or try a stronger model.")
        print(f"{'#'*60}\n")
