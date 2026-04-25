from dataclasses import dataclass, field, asdict

@dataclass
class DailyLog:
    """Log harian untuk satu user."""
    log_date: str  # ISO format YYYY-MM-DD

    # Food: dict[kategori, count] -- berapa kali kategori ini dimakan hari itu.
    # Contoh: {"susu": 2, "gorengan": 1}. Kategori yang tidak ada = 0.
    food: dict[str, int] = field(default_factory=dict)

    # Symptom scores (0-2 atau sesuai skala). Hanya field yang relevan dengan
    # goal user yang perlu diisi; sisanya boleh None.
    symptoms: dict[str, float] = field(default_factory=dict)

    # Habit
    habits: dict[str, float] = field(default_factory=dict)


@dataclass
class CorrelationResult:
    """Hasil korelasi 1 trigger -> 1 symptom dengan lag tertentu."""
    trigger: str          # nama food/habit
    trigger_type: str     # "food" | "habit"
    symptom: str          # field name
    lag_days: int         # 1, 2, atau 3
    correlation: float    # -1 .. 1
    n_samples: int        # jumlah pasangan data (penting untuk reliability)
    direction: str        # "memperburuk" | "memperbaiki"


@dataclass
class Insight:
    """Insight final yang di-generate LLM, siap ditampilkan ke user."""
    headline: str          # 1 kalimat catchy
    explanation: str       # 2-3 kalimat penjelasan
    confidence: str        # "rendah" | "sedang" | "tinggi"
    recommendation: str    # 1 actionable suggestion
    related_trigger: str   # food/habit yang terlibat
    related_symptom: str   # symptom yang terdampak
    lag_days: int
