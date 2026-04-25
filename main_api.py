from fastapi import APIRouter, FastAPI
from typing import List

import uvicorn
from models.schemas import DailyLog
from services.analyzer import analyze_user_logs, weekly_report
from utils.formatter import humanize_insight
from uvicorn import run
from services.analyzer import calculate_symptom_trends 

router = APIRouter()

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


@app.post("/summary/trends")
def get_symptom_trends(logs: List[DailyLog]):
    # 1. Kasih datanya ke "dapur" buat dihitung
    hasil_rekap = calculate_symptom_trends(logs)

    # 2. Kasih balikan ke Flutter
    return {
        "status": "success",
        "chart_data": hasil_rekap
    }

@app.post("/summary/weekly-report")
def get_weekly_report(logs: List[DailyLog]):
    if not logs:
        return {"status": "error", "message": "Belum ada data untuk minggu ini."}
        
    report = weekly_report(logs, user_goals=["jerawat", "rambut_rontok"])
    
    return {
        "status": "success",
        "report": report
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)