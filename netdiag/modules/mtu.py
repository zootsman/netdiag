"""
mtu.py

Performs MTU discovery.
"""

import asyncio
from ..utils import ping_with_size

async def run_mtu_check(config: dict) -> dict:
    """
    Runs MTU discovery using a binary search method.
    """
    mtu_cfg = config.get("mtu_check", {})
    
    results = {
        "check_enabled": mtu_cfg.get("enabled", False),
        "host": mtu_cfg.get("host"),
        "found_mtu": None,
        "message": "MTU проверка не выполнялась."
    }

    if not results["check_enabled"]:
        results["message"] = "MTU проверка отключена в конфигурации."
        return results

    host = mtu_cfg.get("host")
    start_size = mtu_cfg.get("start_size", 1400)
    end_size = mtu_cfg.get("end_size", 1500)
    timeout = config.get("timeout", 5)

    if not host:
        results["message"] = "Хост для проверки MTU не указан в конфигурации."
        return results

    # Binary search for MTU
    low = start_size
    high = end_size
    optimal_mtu = None

    while low <= high:
        mid = (low + high) // 2
        # Ping size is the IP payload. For actual MTU, we need to add IP/ICMP headers (usually 28 bytes)
        # However, ping -s argument often refers to payload, so we test with that.
        # Max payload for common Ethernet MTU 1500 is 1472 (1500 - 20 IP - 8 ICMP)
        # So we test up to 1472.
        
        # Adjusting ping size for MTU discovery. ping -s specifies payload size.
        # Ethernet MTU 1500 = 1472 bytes payload + 28 bytes IP/ICMP header
        
        ping_successful = await ping_with_size(host, mid, timeout)

        if ping_successful:
            optimal_mtu = mid + 28 # Assuming common IP/ICMP header size
            low = mid + 1
        else:
            high = mid - 1
            
    if optimal_mtu:
        results["found_mtu"] = optimal_mtu
        results["message"] = f"Оптимальный MTU для {host}: {optimal_mtu} байт."
    else:
        results["message"] = f"Не удалось определить MTU для {host} в диапазоне {start_size}-{end_size}."

    return results
