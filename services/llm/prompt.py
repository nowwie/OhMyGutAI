from models.schemas import CorrelationResult
from config.settings import SYMPTOM_SCALE_DESCRIPTION

def _format_correlations_for_prompt(
    correlations: list[CorrelationResult],
    n_days: int,
    user_goals: list[str],
) -> str:
    """Format temuan statistik jadi tabel ringkas untuk LLM."""
    lines = [
        f"Data user: {n_days} hari log.",
        f"Goal user: {', '.join(user_goals)}.",
        "",
        "Korelasi signifikan yang ditemukan (sudah dihitung dengan Pearson, "
        "lag 1-3 hari sudah dipertimbangkan):",
        "",
    ]
    if not correlations:
        lines.append("(tidak ada korelasi signifikan)")
        return "\n".join(lines)

    lines.append("| Trigger | Tipe | Symptom | Lag | Korelasi (r) | n | Arah |")
    lines.append("|---|---|---|---|---|---|---|")
    for c in correlations:
        lines.append(
            f"| {c.trigger} | {c.trigger_type} | {c.symptom} "
            f"| {c.lag_days}d | {c.correlation:+.2f} | {c.n_samples} | {c.direction} |"
        )

    lines.append("")
    lines.append("Skala symptom yang dipakai:")
    used_symptoms = {c.symptom for c in correlations}
    for s in used_symptoms:
        if s in SYMPTOM_SCALE_DESCRIPTION:
            lines.append(f"- {s}: {SYMPTOM_SCALE_DESCRIPTION[s]}")
    return "\n".join(lines)
