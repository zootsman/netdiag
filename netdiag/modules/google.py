"""
google.py

Функции для проверок, связанных с Google.
"""
import asyncio
from ..logger import info, warning, error
from ..utils import http_get, check_service_connectivity, check_domain_reachability

async def run_google_checks(timeout=10):
    info("Запуск проверок Google...")
    google_status, _ = await http_get("https://www.google.com", timeout=timeout)
    youtube_status, _ = await http_get("https://www.youtube.com", timeout=timeout)
    google_ok = google_status == 200
    youtube_ok = youtube_status == 200
    return {"google_connectivity": {"status": google_ok}, "youtube_connectivity": {"status": youtube_ok}, "connectivity": google_ok}
