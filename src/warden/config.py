"""Defaults: model IDs, concurrency, budgets, paths.

Models are open-source only via OpenRouter (no vendor models — see CLAUDE.md).
Costs as of fetch: deepseek-chat-v3.1 = $0.15/$0.75 per 1M tokens (in/out);
qwen3-235b-a22b-2507 = $0.071/$0.10 per 1M tokens (in/out).
"""
from __future__ import annotations
from pathlib import Path

# Models
TARGET_MODEL = "deepseek/deepseek-chat-v3.1"
JUDGE_MODEL  = "qwen/qwen3-235b-a22b-2507"

# OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Generation
MAX_TARGET_TOKENS = 800
MAX_JUDGE_TOKENS  = 400
TEMPERATURE_TARGET = 0.7
TEMPERATURE_JUDGE  = 0.0

# Orchestration
CONCURRENCY = 10
MAX_RETRIES = 5
RETRY_INITIAL_DELAY = 2.0
RETRY_MAX_DELAY = 30.0
REQUEST_TIMEOUT = 90.0

# Cost guard (USD; aborts run if exceeded)
COST_CAP_USD = 4.0

# Pricing table (USD per token). Add a row when introducing a new target/judge.
PRICING = {
    "deepseek/deepseek-chat-v3.1":  {"prompt": 0.15e-6,  "completion": 0.75e-6},
    "deepseek/deepseek-v3.2":       {"prompt": 0.252e-6, "completion": 0.378e-6},
    "z-ai/glm-4.6":                 {"prompt": 0.39e-6,  "completion": 1.90e-6},
    "qwen/qwen3-235b-a22b-2507":    {"prompt": 0.071e-6, "completion": 0.10e-6},
}

# Paths
REPO_ROOT  = Path(__file__).resolve().parents[2]
DATA_DIR   = REPO_ROOT / "data"
ATTACKS_DIR = DATA_DIR / "attacks"
OMNIGUARD_PATH = DATA_DIR / "omniguard.txt"
RESULTS_DIR = REPO_ROOT / "results"
TEMPLATE_DIR = REPO_ROOT / "src" / "warden" / "templates"
