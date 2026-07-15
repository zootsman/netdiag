"""
chatgpt.py

Функции для проверок, связанных с ChatGPT.
"""
import asyncio
from ..logger import info, warning, error
from ..utils import check_service_connectivity, check_domain_reachability

async def run_chatgpt_checks(timeout=10):
    info("Запуск проверок ChatGPT...")
    domains = ["chat.openai.com"]
    results = await check_service_connectivity(domains, timeout=timeout)
    return {"chatgpt_connectivity": {"status": all(results.values())}}
