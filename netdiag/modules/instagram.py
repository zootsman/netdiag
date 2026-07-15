"""
instagram.py

Функции для проверок, связанных с Instagram.
"""
import asyncio
from ..logger import info, warning, error
from ..utils import check_service_connectivity, check_domain_reachability

async def run_instagram_checks(timeout=10):
    info("Запуск проверок Instagram...")
    domains = ["www.instagram.com"]
    results = await check_service_connectivity(domains, timeout=timeout)
    return {"instagram_connectivity": {"status": all(results.values())}}
