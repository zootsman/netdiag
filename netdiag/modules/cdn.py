"""
cdn.py

Checks for CDN presence and associated information.
"""

import httpx
from ..utils import http_get

async def check_cdn_info(ip_address: str, timeout: int) -> dict:
    """
    Checks for CDN presence for the given IP address,
    focusing on Cloudflare detection initially.
    
    Returns a dictionary with CDN information.
    """
    results = {
        "cdn_detected": False,
        "provider": None,
        "edge_location": None,
        "country": None,
        "message": "CDN не обнаружен или не удалось определить."
    }

    # Cloudflare CDN detection
    try:
        url = "https://www.cloudflare.com/cdn-cgi/trace"
        status_code, response_text = await http_get(url, timeout=timeout)

        if status_code == 200:
            # Check for cf-railgun, cf-cache-status, etc. to confirm Cloudflare
            if "CF-RAY" in response_text or "cf-request-id" in response_text:
                results["cdn_detected"] = True
                results["provider"] = "Cloudflare"
                results["message"] = "Обнаружен CDN Cloudflare."

                # Extract relevant info from trace_data
                for line in response_text.splitlines():
                    if line.startswith("loc="):
                        results["country"] = line.split("=")[1].strip()
                    elif line.startswith("colo="):
                        results["edge_location"] = line.split("=")[1].strip()
            
            # Additional check for Cloudflare's edge locations
            # This would require more sophisticated parsing of a larger dataset,
            # so for now, we rely on the trace data.

    except Exception as e:
        results["message"] = f"Ошибка при проверке Cloudflare CDN: {e}"

    return results