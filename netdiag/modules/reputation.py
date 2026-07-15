"""
reputation.py

Checks IP reputation using an external API.
"""

import json
from ..utils import http_get
import asyncio

async def _check_ipinfo_io(ip_address: str, timeout: int) -> dict:
    results = {"provider": "ipinfo.io", "vpn": False, "proxy": False, "tor": False, "hosting": False, "message": "", "has_error": False}
    url = f"https://ipinfo.io/{ip_address}/privacy"
    status_code, response_text = await http_get(url, timeout=timeout)

    if status_code == 200:
        try:
            data = json.loads(response_text)
            results.update({
                "vpn": data.get("vpn", False),
                "proxy": data.get("proxy", False),
                "tor": data.get("tor", False),
                "hosting": data.get("hosting", False),
            })
            if any([results["vpn"], results["proxy"], results["tor"], results["hosting"]]):
                results["message"] = "Обнаружены риски"
            else:
                results["message"] = "Риски не обнаружены"
        except json.JSONDecodeError:
            results["message"] = "Ошибка парсинга JSON ответа"
            results["has_error"] = True
    else:
        results["has_error"] = True
        if status_code == 429:
            results["message"] = "Ошибка: превышен лимит запросов к API"
        else:
            results["message"] = f"Ошибка запроса к API (статус: {status_code})"
    return results

async def _check_ipapi_co(ip_address: str, timeout: int) -> dict:
    results = {"provider": "ipapi.co", "vpn": False, "proxy": False, "tor": False, "hosting": False, "message": "", "has_error": False}
    url = f"https://ipapi.co/{ip_address}/json/"
    status_code, response_text = await http_get(url, timeout=timeout)

    if status_code == 200:
        try:
            data = json.loads(response_text)
            if data.get("error"):
                results["message"] = f"Ошибка API: {data.get('reason')}"
                results["has_error"] = True
            else:
                results["vpn"] = data.get("security", {}).get("vpn", False)
                results["proxy"] = data.get("security", {}).get("proxy", False)
                results["hosting"] = data.get("security", {}).get("hosting", False)
                results["tor"] = data.get("security", {}).get("tor", False)
                if any([results["vpn"], results["proxy"], results["tor"], results["hosting"]]):
                    results["message"] = "Обнаружены риски"
                else:
                    results["message"] = "Риски не обнаружены"
        except json.JSONDecodeError:
            results["message"] = "Ошибка парсинга JSON ответа"
            results["has_error"] = True
    else:
        results["has_error"] = True
        if status_code == 429:
            results["message"] = "Ошибка: превышен лимит запросов к API (Too Many Requests)"
        else:
            results["message"] = f"Ошибка запроса к API (статус: {status_code})"
    return results

async def _check_ip_api_com(ip_address: str, timeout: int) -> dict:
    results = {"provider": "ip-api.com", "vpn": False, "proxy": False, "tor": False, "hosting": False, "message": "", "has_error": False}
    url = f"http://ip-api.com/json/{ip_address}?fields=proxy,hosting"
    status_code, response_text = await http_get(url, timeout=timeout)

    if status_code == 200:
        try:
            data = json.loads(response_text)
            results["proxy"] = data.get("proxy", False)
            results["hosting"] = data.get("hosting", False)
            if any([results["proxy"], results["hosting"]]):
                results["message"] = "Обнаружены риски"
            else:
                results["message"] = "Риски не обнаружены"
        except json.JSONDecodeError:
            results["message"] = "Ошибка парсинга JSON ответа"
            results["has_error"] = True
    else:
        results["has_error"] = True
        if status_code == 429:
            results["message"] = "Ошибка: превышен лимит запросов к API"
        else:
            results["message"] = f"Ошибка запроса к API (статус: {status_code})"
    return results

async def check_ip_reputation(ip_address: str, config: dict) -> dict:
    """
    Checks IP reputation using multiple external providers.
    Aggregates results for VPN, proxy, Tor, and hosting detection.
    """
    reputation_cfg = config.get("reputation", {})
    
    overall_results = {
        "check_enabled": reputation_cfg.get("enabled", False),
        "overall_vpn": False,
        "overall_proxy": False,
        "overall_tor": False,
        "overall_hosting": False,
        "providers_data": [],
        "message": "Проверка репутации отключена в конфигурации.",
        "is_privacy_risk": False
    }

    if not overall_results["check_enabled"]:
        return overall_results

    timeout = config.get("timeout", 5)

    provider_checks = [
        _check_ipinfo_io(ip_address, timeout),
        _check_ipapi_co(ip_address, timeout),
        _check_ip_api_com(ip_address, timeout)
    ]

    raw_results = await asyncio.gather(*provider_checks, return_exceptions=True)

    flagged_issues = []
    
    for res in raw_results:
        if isinstance(res, Exception):
            overall_results["providers_data"].append({"provider": "unknown", "message": f"Ошибка выполнения: {res}"})
            continue

        overall_results["providers_data"].append(res)

        if res.get("vpn"): overall_results["overall_vpn"] = True
        if res.get("proxy"): overall_results["overall_proxy"] = True
        if res.get("tor"): overall_results["overall_tor"] = True
        if res.get("hosting"): overall_results["overall_hosting"] = True

    privacy_issues_list = []
    if overall_results["overall_vpn"]: privacy_issues_list.append("VPN")
    if overall_results["overall_proxy"]: privacy_issues_list.append("Прокси")
    if overall_results["overall_tor"]: privacy_issues_list.append("Tor")
    if overall_results["overall_hosting"]: privacy_issues_list.append("Хостинг")

    if privacy_issues_list:
        overall_results["message"] = f"Обнаружено: {', '.join(privacy_issues_list)}."
        overall_results["is_privacy_risk"] = True
    else:
        overall_results["message"] = "Признаков VPN/прокси не обнаружено."
        overall_results["is_privacy_risk"] = False

    return overall_results
