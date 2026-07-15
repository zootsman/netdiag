import httpx
from ..utils import http_get
import asyncio
import re


async def get_public_ip(timeout=5):
    """
    Tries to get the public IP from a list of providers.
    """
    providers = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
        "https://api.my-ip.io/ip",
    ]

    tasks = [http_get(url, timeout=timeout) for url in providers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, tuple) and result[0] == 200:  # result[0] is status_code
            ip = result[1].strip()
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                return ip

    return None