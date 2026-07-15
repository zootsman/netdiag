"""
tls.py

Performs SSL/TLS certificate checks.
"""

import asyncio
import ssl
from datetime import datetime, timedelta

async def get_certificate_details(host: str, port: int = 443, timeout: int = 5) -> dict:
    """
    Connects to a host and retrieves its SSL certificate details.
    """
    results = {"host": host, "port": port, "status": "fail", "error": None}
    
    try:
        # Create a default SSL context
        context = ssl.create_default_context()
        
        # Open connection
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=context),
            timeout=timeout
        )
        
        # Get the certificate
        peercert = writer.get_extra_info('peercert')
        writer.close()
        await writer.wait_closed()

        if not peercert:
            results["error"] = "Не удалось получить сертификат от узла."
            return results

        # Parse the certificate
        issuer = dict(x[0] for x in peercert.get('issuer', []))
        subject = dict(x[0] for x in peercert.get('subject', []))
        
        not_after_str = peercert.get('notAfter')
        if not_after_str:
            expiry_date = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
        else:
            expiry_date = None

        results.update({
            "status": "ok",
            "issuer": issuer.get("organizationName", "N/A"),
            "subject": subject.get("commonName", "N/A"),
            "expires": expiry_date,
            "serial_number": peercert.get("serialNumber")
        })

    except (asyncio.TimeoutError, ConnectionRefusedError, OSError, ssl.SSLError) as e:
        results["error"] = f"Ошибка подключения/SSL: {e}"
    except Exception as e:
        results["error"] = f"Неизвестная ошибка: {e}"
        
    return results


async def run_tls_analysis(config: dict) -> dict:
    """
    Runs a series of TLS certificate checks based on the configuration.
    """
    tls_cfg = config.get("tls_check", {})
    
    results = {
        "check_enabled": tls_cfg.get("enabled", False),
        "hosts": {}
    }

    if not results["check_enabled"]:
        return results

    check_hosts = tls_cfg.get("check_hosts", [])
    timeout = config.get("timeout", 5)
    
    tasks = [get_certificate_details(host, timeout=timeout) for host in check_hosts]
    
    analysis_results = await asyncio.gather(*tasks)
    
    for res in analysis_results:
        results["hosts"][res["host"]] = res
        
    return results
