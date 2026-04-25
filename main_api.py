from fastapi import FastAPI
from typing import List

import uvicorn
from models.schemas import DailyLog
from services.analyzer import analyze_user_logs
from utils.formatter import humanize_insight
from uvicorn import run

app = FastAPI(
    title="OhMyGut AI Analysis Gut Health",
    description="AI yang digunakan untuk menganalisis data harian pengguna dan memberikan insight terkait kesehatan pencernaan usus berdasarkan data makanan dan gaya hidup.",
    version="1.0.0",
)

# 🔹 endpoint kirim log dari Flutter
@app.post("/log")
def save_logs(logs: List[DailyLog]):
    # sementara kita return dulu
    return {
        "status": "received",
        "total_logs": len(logs)
    }


# 🔹 endpoint ANALISIS (INI YANG PENTING)
@app.post("/analyze")
def analyze(logs: List[DailyLog]):

    result = analyze_user_logs(
        logs=logs,
        user_goals=["jerawat", "rambut_rontok"]
    )

    # 🔥 ubah ke bahasa manusia
    result["insights_ui"] = [
        humanize_insight(i)
        for i in result.get("insights", [])
    ]

    return result

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)