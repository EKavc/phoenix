"""
Phoenix — entry point
Test case: healthcare data sharing between hospitals with GDPR compliance
"""

from phoenix import Phoenix

PROBLEM = """
Design a system for sharing healthcare data between hospitals in Slovakia
that maintains GDPR compliance, data sovereignty for each hospital,
and enables clinical research without a central data repository.
The solution must be feasible with existing NIS systems.
"""

if __name__ == "__main__":
    phoenix = Phoenix(problem=PROBLEM.strip())
    result = phoenix.run()
