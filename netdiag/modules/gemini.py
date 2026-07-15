"""
gemini.py

Функции для проверок, связанных с Google Gemini.
"""
import asyncio
from ..logger import info, warning, error
from ..utils import check_service_connectivity, check_domain_reachability

async def run_gemini_checks(timeout=10):
    info("Запуск проверок Gemini...")
    domains = ["gemini.google.com"]
    results = await check_service_connectivity(domains, timeout=timeout)
    return {"gemini_connectivity": {"status": all(results.values())}}
