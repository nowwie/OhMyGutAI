from models.schemas import DailyLog, CorrelationResult
from config.settings import FOOD_CATEGORIES, LAG_DAYS, HABIT_FIELDS, CORRELATION_THRESHOLD
from datetime import date, timedelta
from collections import defaultdict
from typing import Any

def _group_by_date(logs: list[DailyLog]) -> dict[str, DailyLog]:
    """Gabungkan multiple entries per hari jadi 1 DailyLog."""
    grouped = defaultdict(list)
    for log in logs:
        grouped[log.log_date].append(log)

    merged = {}
    for date_str, day_logs in grouped.items():
        merged_food = {}
        merged_habits = {}
        merged_symptoms = {}
        for l in day_logs:
            merged_food.update(l.food)
            merged_habits.update(l.habits)
            merged_symptoms.update(l.symptoms)
        merged[date_str] = DailyLog(
            log_date=date_str,
            food=merged_food,
            habits=merged_habits,
            symptoms=merged_symptoms,
        )
    return merged

def _pearson(x: list[float], y: list[float]) -> float:
    """Pearson correlation tanpa numpy (supaya zero-dependency)."""
    n = len(x)
    if n < 2:
        return 0.0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
    den_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def _build_series(
    logs: list[DailyLog],
    trigger_extractor,        # callable(log) -> float | None
    symptom_field: str,
    lag: int,
) -> tuple[list[float], list[float]]:
    """Bangun pasangan (trigger pada hari T, symptom pada hari T+lag)."""
    # Index logs by date for easy lookup
    # by_date: dict[str, DailyLog] = {log.log_date: log for log in logs}
    by_date = _group_by_date(logs)
    sorted_dates = sorted(by_date.keys())

    xs: list[float] = []
    ys: list[float] = []
    for d_str in sorted_dates:
        trigger_val = trigger_extractor(by_date[d_str])
        if trigger_val is None:
            continue
        # Hitung tanggal target untuk symptom
        target_date = (date.fromisoformat(d_str) + timedelta(days=lag)).isoformat()
        target_log = by_date.get(target_date)
        if target_log is None:
            continue
        symptom_val = target_log.symptoms.get(symptom_field)
        if symptom_val is None:
            continue
        xs.append(float(trigger_val))
        ys.append(float(symptom_val))
    return xs, ys


def compute_correlations(
    logs: list[DailyLog],
    symptom_fields: list[str],
) -> list[CorrelationResult]:
    """Hitung semua korelasi food/habit x symptom x lag, return yang signifikan."""
    results: list[CorrelationResult] = []

    triggers: list[tuple[str, str, Any]] = []
    # Food triggers
    for cat in FOOD_CATEGORIES:
        triggers.append((cat, "food", lambda log, c=cat: log.food.get(c, 0)))
    # Habit triggers
    for habit in HABIT_FIELDS:
        triggers.append((habit, "habit", lambda log, h=habit: log.habits.get(h)))

    for trigger_name, trigger_type, extractor in triggers:
        for symptom in symptom_fields:
            for lag in LAG_DAYS:
                xs, ys = _build_series(logs, extractor, symptom, lag)
                if len(xs) < 2:  # butuh min 3 pasangan supaya korelasi bermakna
                    continue
                # Skip kalau trigger tidak pernah bervariasi (selalu 0 atau konstan)
                if len(set(xs)) < 2:
                    continue
                r = _pearson(xs, ys)
                if abs(r) < CORRELATION_THRESHOLD:
                    continue
                results.append(CorrelationResult(
                    trigger=trigger_name,
                    trigger_type=trigger_type,
                    symptom=symptom,
                    lag_days=lag,
                    correlation=round(r, 3),
                    n_samples=len(xs),
                    direction="memperburuk" if r > 0 else "memperbaiki",
                ))

    # Sort by absolute correlation desc, ambil top 10 supaya prompt LLM ramping
    results.sort(key=lambda r: abs(r.correlation), reverse=True)
    return results[:10]