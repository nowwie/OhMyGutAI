import math
from models.schemas import DailyLog, CorrelationResult
from config.settings import FOOD_CATEGORIES, LAG_DAYS, HABIT_FIELDS, CORRELATION_THRESHOLD
from typing import Any

def _pearson(x: list[float], y: list[float]) -> float:
    """Pearson correlation tanpa numpy (zero-dependency)."""
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
    trigger_extractor,
    symptom_field: str,
    lag: int,
) -> tuple[list[float], list[float]]:
    """
    Bangun pasangan data berdasarkan URUTAN input (Sesi).
    Lag 0 = trigger & symptom di sesi yang sama.
    Lag 1 = trigger di sesi i, symptom di sesi berikutnya (i+1).
    """
    xs: list[float] = []
    ys: list[float] = []

    # Kita pakai urutan list (i), bukan tanggal (date)
    # Ini kuncinya supaya input 3-5x sehari tetep bisa dihitung
    for i in range(len(logs) - lag):
        trigger_val = trigger_extractor(logs[i])
        symptom_val = logs[i + lag].symptoms.get(symptom_field)

        if trigger_val is not None and symptom_val is not None:
            xs.append(float(trigger_val))
            ys.append(float(symptom_val))
            
    return xs, ys


def compute_correlations(
    logs: list[DailyLog],
    symptom_fields: list[str],
) -> list[CorrelationResult]:
    """Hitung korelasi berdasarkan urutan entri (intra-day support)."""
    results: list[CorrelationResult] = []

    # Pastikan logs terurut berdasarkan waktu input (jika diperlukan)
    # logs.sort(key=lambda x: x.log_date) 

    triggers: list[tuple[str, str, Any]] = []
    # Food triggers
    for cat in FOOD_CATEGORIES:
        triggers.append((cat, "food", lambda log, c=cat: log.food.get(c, 0)))
    # Habit triggers
    for habit in HABIT_FIELDS:
        triggers.append((habit, "habit", lambda log, h=habit: log.habits.get(h, 0)))

    for trigger_name, trigger_type, extractor in triggers:
        for symptom in symptom_fields:
            for lag in LAG_DAYS:
                # SEKARANG: Pakai urutan list, bukan tanggal
                xs, ys = _build_series(logs, extractor, symptom, lag)
                
                # Butuh minimal 3 pasang data biar korelasi nggak asal-asalan
                if len(xs) < 3: 
                    continue
                    
                # Skip kalau angkanya itu-itu aja (nggak bervariasi)
                if len(set(xs)) < 2 or len(set(ys)) < 2:
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

    # Ambil top 10 korelasi terkuat
    results.sort(key=lambda r: abs(r.correlation), reverse=True)
    return results[:10]