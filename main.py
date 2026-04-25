# # 

# """
# OhMyGut AI - Correlation engine for food/habit -> symptom analysis.

# Flow:
#   1. Frontend kirim 14 hari log per user (food, symptom, habit).
#   2. Modul ini melakukan:
#      a. Pre-analysis statistik (Pearson correlation) dengan lag 1-3 hari.
#      b. Filter top-N korelasi paling signifikan.
#      c. Kirim ringkasan ke LLM untuk generate insight natural language
#         + rekomendasi actionable, via tool-calling (structured output).
#   3. Return list insight siap ditampilkan di dashboard.

# Usage (sebagai library):
#     from ohmygut_ai import analyze_user_logs
#     insights = analyze_user_logs(user_logs, user_goals=["jerawat"])

# Usage (CLI demo dengan synthetic data):
#     python ohmygut_ai.py --demo
#     python ohmygut_ai.py --input logs.json --goals jerawat,rambut_rontok
# """

# from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import Any

import requests
# ---------------------------------------------------------------------------
# CLI / Demo
# ---------------------------------------------------------------------------

from models.schemas import DailyLog
from config.settings import DEFAULT_MODEL
from services.analyzer import analyze_user_logs

def _generate_demo_logs(n_days: int = 14, seed: int = 42) -> list[DailyLog]:
    """
    Generate synthetic 14-day log dengan pola tertanam:
      - Susu (food) -> skin_score memburuk dengan lag 2 hari (korelasi kuat)
      - Stress level -> hair_loss_score memburuk dengan lag 1 hari
      - Air putih banyak -> skin_score membaik dengan lag 1 hari
    Supaya demo juri langsung kelihatan AI bisa nemu pola ini.
    """
    import random
    rng = random.Random(seed)

    start = date.today() - timedelta(days=n_days - 1)
    logs: list[DailyLog] = []

    # Pre-generate sequences agar bisa lookback untuk efek lag
    milk_seq = [rng.choice([0, 0, 1, 2]) for _ in range(n_days)]
    fastfood_seq = [rng.choice([0, 0, 1]) for _ in range(n_days)]
    fried_seq = [rng.choice([0, 1, 1, 2]) for _ in range(n_days)]
    veg_seq = [rng.choice([0, 1, 2, 2]) for _ in range(n_days)]
    water_seq = [rng.randint(2, 10) for _ in range(n_days)]
    stress_seq = [rng.randint(1, 3) for _ in range(n_days)]
    sleep_seq = [round(rng.uniform(4.5, 8.5), 1) for _ in range(n_days)]

    for i in range(n_days):
        d = (start + timedelta(days=i)).isoformat()

        # Symptom hari ini = fungsi dari trigger 1-3 hari lalu + noise
        skin = 0.0
        hair = 0.0

        # Susu 2 hari lalu memperburuk kulit (efek kuat)
        if i >= 2:
            skin += milk_seq[i - 2] * 0.8
        # Air putih kemarin memperbaiki kulit
        if i >= 1:
            skin -= (water_seq[i - 1] - 5) * 0.15
        # Fast food 1 hari lalu memperburuk kulit
        if i >= 1:
            skin += fastfood_seq[i - 1] * 0.5
        # Stress kemarin memperburuk rambut rontok
        if i >= 1:
            hair += (stress_seq[i - 1] - 1) * 0.6
        # Tidur kurang kemarin -> rambut rontok
        if i >= 1 and sleep_seq[i - 1] < 6:
            hair += 0.5

        # Noise
        skin += rng.uniform(-0.3, 0.3)
        hair += rng.uniform(-0.3, 0.3)

        # Clamp ke skala 0-2
        skin_score = max(0.0, min(2.0, round(skin)))
        hair_score = max(0.0, min(2.0, round(hair)))

        logs.append(DailyLog(
            log_date=d,
            food={
                "susu": milk_seq[i],
                "fast_food": fastfood_seq[i],
                "gorengan": fried_seq[i],
                "sayur": veg_seq[i],
                "nasi": rng.choice([1, 2, 2]),
                "buah": rng.choice([0, 1, 1]),
            },
            symptoms={
                "skin_score": skin_score,
                "hair_loss_score": hair_score,
            },
            habits={
                "sleep_hours": sleep_seq[i],
                "exercise": rng.choice([0, 0, 1]),
                "stress_level": stress_seq[i],
                "water_glasses": water_seq[i],
            },
        ))
    return logs


def _logs_from_dict(raw: list[dict]) -> list[DailyLog]:
    return [DailyLog(**item) for item in raw]


def main() -> int:
    parser = argparse.ArgumentParser(description="OhMyGut AI correlation engine")
    parser.add_argument("--demo", action="store_true",
                        help="Pakai synthetic 14-day data dengan pola tertanam.")
    parser.add_argument("--input", type=str,
                        help="Path JSON file berisi list DailyLog.")
    parser.add_argument("--goals", type=str, default="jerawat,rambut_rontok",
                        help="Comma-separated goals dari onboarding.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--output", type=str,
                        help="Path output JSON. Kalau tidak ada, print ke stdout.")
    parser.add_argument("--no-llm", action="store_true",
                        help="Skip LLM call, hanya return korelasi mentah.")
    args = parser.parse_args()

    if not args.demo and not args.input:
        parser.error("Sebutkan --demo atau --input")

    if args.demo:
        logs = _generate_demo_logs()
    else:
        with open(args.input) as f:
            logs = _logs_from_dict(json.load(f))

    goals = [g.strip() for g in args.goals.split(",") if g.strip()]

    result = analyze_user_logs(logs, goals, model=args.model)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())