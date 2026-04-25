TRIGGER_LABELS = {
    "water_glasses": "air putih",
    "sleep_hours": "jam tidur",
    "stress_level": "tingkat stres",
    "fast_food": "fast food",
    "susu": "susu",
    "sayur": "sayur",
}

SYMPTOM_LABELS = {
    "skin_score": "kondisi kulit",
    "hair_loss_score": "rambut rontok",
    "bloating_score": "perut kembung",
    "energy_score": "energi",
    "mood_score": "mood",
}

# def humanize_insight(insight):
#     trigger = TRIGGER_LABELS.get(insight.get("related_trigger", "tidak diketahui"),"tidak diketahui")
#     symptom = SYMPTOM_LABELS.get(insight.get("related_symptom", "tidak diketahui"), "tidak diketahui")
#     lag = insight.get("lag_days", 0)

#     return {
#         "title": insight.get("headline", "Tidak diketahui"),
#         "desc": insight.get("explanation", "Tidak diketahui"),
#         "simple_explanation": f"{trigger} berhubungan dengan {symptom} sekitar {lag} hari setelahnya.",
#         "recommendation": insight.get("recommendation", "Tidak diketahui"),
#         "confidence": insight.get("confidence", 0),
#     }


def humanize_insight(insight: dict) -> dict:
    trigger = TRIGGER_LABELS.get(
        insight.get("related_trigger", ""),
        insight.get("related_trigger", "tidak diketahui")
    )
    symptom = SYMPTOM_LABELS.get(
        insight.get("related_symptom", ""),
        insight.get("related_symptom", "tidak diketahui")
    )

    return {
        "title": insight.get("headline", "Pola ditemukan"),
        "desc": insight.get("explanation", ""),
        "simple_explanation": f"{trigger} berhubungan dengan {symptom} sekitar {insight.get('lag_days', '?')} hari setelahnya.",
        "recommendation": insight.get("recommendation", ""),
        "confidence": insight.get("confidence", "sedang"),
    }