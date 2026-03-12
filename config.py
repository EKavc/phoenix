"""
Phoenix configuration — one file, one place to change
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Models ────────────────────────────────────────────────────────────────────
MAIN_MODEL = "claude-haiku-4-5-20251001" # Alchemist — testing only, switch back to claude-opus-4-6
FAST_MODEL = "claude-haiku-4-5-20251001" # Regular agents + Curator — fast evaluations

# ── API ───────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ── Guardian — thresholds ─────────────────────────────────────────────────────
ENTROPY_DROP_THRESHOLD    = 0.10   # entropy drop > 10% triggers signal
DELTA_QUALITY_THRESHOLD   = 0.05   # delta quality < 5% = stagnation
MIN_ROUNDS_BEFORE_CHAOS   = 5      # minimum rounds before first Chaos
QUALITY_RISING_FOR_SOL    = 0.15   # quality must rise > 15% for Sol
QUALITY_SUSTAINED_FOR_SOL = 0.75   # quality > 75% for 4+ rounds -> Sol
GOLD_PLATING_MAX_QUALITY  = 0.65   # gold-plating only fires below this threshold
WALL_QUALITY_CEILING      = 0.30   # avg quality below this = agents hitting a wall
WALL_DIVERSITY_FLOOR      = 0.70   # avg diversity above this = agents still trying
WALL_ROUNDS               = 5      # how many rounds of wall before CHAOS

# ── Alchemist ─────────────────────────────────────────────────────────────────
ALCHEMIST_MAX_ATTEMPTS = 3       # magic number — three attempts
ARXIV_MAX_RESULTS      = 5       # number of papers from arxiv

# ── System ────────────────────────────────────────────────────────────────────
MAX_ROUNDS = 20                  # safety limit
