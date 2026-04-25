# LOVABLE_AI_URL = "https://ai.gateway.lovable.dev/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash"

# Lag yang dipertimbangkan: efek makanan ke gejala butuh 1-3 hari
LAG_DAYS = [1, 2, 3]

# Minimum data point supaya korelasi tidak noise. Kalau user baru log 5 hari,
# kita tidak generate insight palsu.
MIN_DAYS_FOR_ANALYSIS = 3

# Threshold korelasi absolut untuk dianggap "menarik untuk dianalisis LLM"
CORRELATION_THRESHOLD = 0.2

# Mapping goal -> field symptom yang relevan
GOAL_TO_SYMPTOM_FIELD = {
    "jerawat": "skin_score",
    "rambut_rontok": "hair_loss_score",
    "kembung": "bloating_score",
    "lelah": "energy_score",
    "berat_badan": "weight_score",
    "mood": "mood_score",
}

# Skala symptom: semakin tinggi = semakin parah/buruk (kecuali energy & mood
# yang dibalik supaya konsisten).
SYMPTOM_SCALE_DESCRIPTION = {
    "skin_score": "0=clear, 1=1-2 jerawat baru, 2=breakout parah",
    "hair_loss_score": "0=normal, 1=lebih dari biasa, 2=banyak banget",
    "bloating_score": "0=tidak ada, 1=sedikit, 2=parah",
    "energy_score": "0=energik, 1=biasa, 2=lelah berat",
    "weight_score": "0=stabil/turun, 1=naik sedikit, 2=naik banyak",
    "mood_score": "0=stabil, 1=naik-turun, 2=buruk",
}

# Kategori food & habit yang akan diuji korelasinya
FOOD_CATEGORIES = [
    "gorengan", "nasi", "sayur", "buah", "susu", "daging",
    "gula_manis", "tepung_roti", "fast_food", "minuman_manis", "air_putih",
]

HABIT_FIELDS = [
    "sleep_hours",      # numeric
    "exercise",         # 0/1
    "stress_level",     # 1-3
    "water_glasses",    # numeric
]
