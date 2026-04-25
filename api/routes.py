
from fastapi import APIRouter
from services.analyzer import analyze_user_logs
from models.schemas import DailyLog
from utils.formatter import humanize_insight

router = APIRouter()

@router.get("/analyze/{user_id}")
def analyze(user_id: str):
    # ambil data
    # panggil analyzer
    return result