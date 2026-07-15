"""
icmp.py

Performs ICMP tests like ping and traceroute.
"""

import asyncio
from ..utils import ping_host, run_command

async def run_icmp_analysis(config: dict) -> dict:
    """
    Runs a series of ICMP tests based on the configuration.
    """
    icmp_cfg = config.get("icmp_analysis", {})
    
    results = {
        "check_enabled": icmp_cfg.get("enabled", False),
        "ping_results": {},
        "traceroute_result": {}
    }

    if not results["check_enabled"]:
        return results

    # --- Ping Tests ---
    ping_hosts = icmp_cfg.get("ping_hosts", [])
    ping_tasks = [ping_host(host) for host in ping_hosts]
    
    ping_run_results = await asyncio.gather(*ping_tasks)
    
    for host, result_ms in zip(ping_hosts, ping_run_results):
        if result_ms is not None:
            results["ping_results"][host] = {"status": "ok", "avg_latency_ms": result_ms}
        else:
            results["ping_results"][host] = {"status": "fail", "error": "Хост недоступен или время запроса истекло."}

    # --- Traceroute Test ---
    traceroute_host = icmp_cfg.get("traceroute_host")
    if traceroute_host:
        # Using platform-specific traceroute arguments can be tricky.
        # -n to avoid resolving names, -w to set wait time.
        # This is a basic implementation.
        command = ["traceroute", "-n", "-w", "3", "-m", "20", traceroute_host]
        timeout = config.get("timeout", 5) * 4 # Give traceroute more time
        
        ok, output = await run_command(command, timeout=timeout)
        
        results["traceroute_result"] = {
            "host": traceroute_host,
            "status": "ok" if ok else "fail",
            "output": output
        }
        
    return results
