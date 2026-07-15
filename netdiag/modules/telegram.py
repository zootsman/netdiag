"""
telegram.py

Функции для проверок, связанных с Telegram.
"""
import asyncio
from ..logger import info, warning, error
from ..utils import check_service_connectivity, check_domain_reachability

async def run_telegram_checks(timeout=10):
    info("Запуск проверок Telegram...")
    domains = ["web.telegram.org"]
    results = await check_service_connectivity(domains, timeout=timeout)
    return {"telegram_connectivity": {"status": all(results.values())}}
