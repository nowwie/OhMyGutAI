
# LLM layer (Lovable AI Gateway, tool calling untuk structured output)

INSIGHT_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "emit_insights",
        "description": (
            "Emit 1-5 insight natural language untuk user, berdasarkan korelasi "
            "statistik yang sudah dihitung. Setiap insight harus actionable, "
            "tidak menakut-nakuti, dan jujur soal confidence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "insights": {
                    "type": "array",
                    "description": "1 sampai 5 insight, urut dari confidence tertinggi.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "headline": {
                                "type": "string",
                                "description": "1 kalimat catchy, max 100 char, gaya friendly. Contoh: '3 dari 4 kali kulitmu breakout terjadi 2 hari setelah konsumsi susu.'",
                            },
                            "explanation": {
                                "type": "string",
                                "description": "2-3 kalimat penjelasan pola, sebut angka korelasi & jumlah hari.",
                            },
                            "confidence": {
                                "type": "string",
                                "enum": ["rendah", "sedang", "tinggi"],
                                "description": "Tinggi jika |r|>0.6 & n>=8. Sedang jika |r| 0.45-0.6. Rendah selainnya.",
                            },
                            "recommendation": {
                                "type": "string",
                                "description": "1 saran konkret yang bisa dicoba 3-7 hari ke depan.",
                            },
                            "related_trigger": {"type": "string"},
                            "related_symptom": {"type": "string"},
                            "lag_days": {
                                "type": "integer",
                                "description": "Lag time dalam hari (1, 2, atau 3).",
                            },
                        },
                        "required": [
                            "headline", "explanation", "confidence",
                            "recommendation", "related_trigger",
                            "related_symptom", "lag_days",
                        ],
                    },
                },
            },
            "required": ["insights"],
        },
    },
}


SYSTEM_PROMPT = """Balas HANYA dalam JSON valid, tanpa teks tambahan.

Format:
{
  "insights": [
    {
      "headline": "...",
      "explanation": "...",
      "confidence": "rendah|sedang|tinggi",
      "recommendation": "...",
      "related_trigger": "...",
      "related_symptom": "...",
      "lag_days": 1
    }
  ]
}
Kamu adalah AI nutritionist & wellness coach untuk app OhMyGut.

Tugasmu: ubah data korelasi statistik (yang sudah dihitung backend) menjadi
insight personal yang actionable dan mudah dipahami remaja/dewasa muda Indonesia.

ATURAN KETAT:
1. JANGAN mengarang korelasi. Hanya gunakan data yang diberikan.
2. JANGAN memberi diagnosis medis. Kamu memberi observasi pola, bukan vonis.
3. Selalu jujur soal confidence. Kalau n_samples < 6, confidence = rendah.
4. Selalu sebut lag time (misal "2 hari setelah") karena ini value utama app.
5. Bahasa: santai, friendly, Indonesia. Hindari istilah medis berat.
6. Kalau korelasi negatif (memperbaiki gejala), framing-nya positif.
7. Maksimal 5 insight. Pilih yang paling actionable & confidence tertinggi.

PANGGIL TOOL emit_insights untuk mengembalikan hasil. Jangan reply text biasa."""

