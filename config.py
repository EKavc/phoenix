"""
Phoenix configuration — one file, one place to change
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Models ────────────────────────────────────────────────────────────────────
MAIN_MODEL = "claude-opus-4-6"           # Alchemist — meta-cognition, heavy lifting
FAST_MODEL = "claude-haiku-4-5-20251001" # Regular agents + Curator — fast evaluations

# ── API ───────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ── Guardian — thresholds ─────────────────────────────────────────────────────
ENTROPY_DROP_THRESHOLD  = 0.15   # entropy drop > 15% triggers signal
DELTA_QUALITY_THRESHOLD = 0.05   # delta quality < 5% = stagnation
MIN_ROUNDS_BEFORE_CHAOS = 3      # minimum rounds before first Chaos
QUALITY_RISING_FOR_SOL  = 0.10   # quality must rise > 10% for Sol

# ── Alchemist ─────────────────────────────────────────────────────────────────
ALCHEMIST_MAX_ATTEMPTS = 3       # magic number — three attempts
ARXIV_MAX_RESULTS      = 5       # number of papers from arxiv

# ── System ────────────────────────────────────────────────────────────────────
MAX_ROUNDS = 20                  # safety limit
