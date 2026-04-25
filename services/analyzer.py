from services.correlation import compute_correlations
from models.schemas import CorrelationResult, Insight, DailyLog
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import Any
import os
from services.llm.llm import _call_gemini
from config.settings import DEFAULT_MODEL, MIN_DAYS_FOR_ANALYSIS, GOAL_TO_SYMPTOM_FIELD
from utils.formatter import humanize_insight

def analyze_user_logs(
    logs: list[DailyLog],
    user_goals: list[str],
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """
    Entry point utama. Dipanggil dari backend (FastAPI/Flask/etc).

    Args:
        logs: list DailyLog (urutan tanggal tidak harus sorted).
        user_goals: ["jerawat", "rambut_rontok", ...] dari onboarding.
        model: override model LLM kalau perlu.

    Returns:
        {
            "status": "ok" | "insufficient_data" | "no_pattern",
            "n_days": int,
            "correlations": [...],   # raw stats untuk debugging/transparansi
            "insights": [...],       # natural-language insights dari LLM
            "message": str,          # human-readable status
        }
    """
    # api_key = api_key or os.environ.get("GEMINI_API_KEY")

    n_days = len({log.log_date for log in logs})
    n_entries = len(logs)

    # if n_days < MIN_DAYS_FOR_ANALYSIS:
    #     return {
    #         "status": "insufficient_data",
    #         "n_days": n_days,
    #         "correlations": [],
    #         "insights": [],
    #         "message": (
    #             f"Baru {n_days} hari data. Lanjut log "
    #             f"{MIN_DAYS_FOR_ANALYSIS - n_days} hari lagi supaya AI bisa "
    #             "mulai mencari pola."
    #         ),
    #     }
    if n_entries < MIN_DAYS_FOR_ANALYSIS:
        return {
            "status": "insufficient_data",
            "n_days":  n_entries,
            "correlations": [],
            "insights": [],
            "message": (
                f"Baru {n_entries} entri data. Lanjut log "
                f"{MIN_DAYS_FOR_ANALYSIS - n_entries} hari lagi supaya AI bisa "
                "mulai mencari pola."
            ),
        }

    # Tentukan symptom fields yang relevan dengan goal
    symptom_fields = [
        GOAL_TO_SYMPTOM_FIELD[g]
        for g in user_goals
        if g in GOAL_TO_SYMPTOM_FIELD
    ]
    if not symptom_fields:
        return {
            "status": "insufficient_data",
            "n_days": n_days,
            "correlations": [],
            "insights": [],
            "message": "Goal user tidak dikenali. Cek mapping GOAL_TO_SYMPTOM_FIELD.",
        }

    # Step 1: stats pre-analysis (deterministic, cepat, hemat token)
    correlations = compute_correlations(logs, symptom_fields)

    if not correlations:
        return {
            "status": "no_pattern",
            "n_days": n_days,
            "correlations": [],
            "insights": [],
            "message": (
                "Belum ada pola yang cukup kuat ditemukan. Coba variasikan "
                "makanan & habit beberapa hari ke depan."
            ),
        }

    # Step 2: LLM untuk natural-language insight

    insights = _call_gemini(
        correlations, n_days, user_goals,
    )

    formatted_insights = [humanize_insight(i) for i in insights]

    return {
        "insights": formatted_insights,
        # "status": "ok",
        # "n_days": n_days,
        # "correlations": [asdict(c) for c in correlations],
        # "insights": formatted_insights,
        # "message": f"Ditemukan {len(insights)} insight dari {n_days} hari data.",
    }
