import asyncio
import os
import re
import subprocess
from datetime import datetime
import httpx

async def ping_with_size(host: str, size: int, timeout: int = 1) -> bool:
    """
    Асинхронно пингует хост с указанным размером пакета и флагом DF.
    Возвращает True, если пинг успешен (пакет не фрагментируется), иначе False.
    """
    try:
        # -M do: Don't Fragment (Linux)
        # -s <size>: packet size
        # -t <timeout>: timeout in seconds
        command = ["ping", "-c", "1", "-M", "do", "-s", str(size), "-W", str(timeout), host]
        ok, _ = await run_command(command, timeout=timeout + 1)
        return ok
    except Exception:
        return False

async def http_get(url: str, timeout: int = 10):
    """
    Асинхронно выполняет GET-запрос и возвращает код состояния и текст ответа.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=timeout)
            return response.status_code, response.text
    except Exception:
        return None, ""

def get_system_dns_servers():
    dns_servers = []
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if line.startswith("nameserver"):
                    dns_servers.append(line.split()[1])
    except FileNotFoundError:
        pass
    return dns_servers

async def check_domain_reachability(domain: str, resolver, timeout: int = 5):
    """
    Checks if a domain is reachable via DNS and HTTP.
    """
    result = {"status": False, "message": ""}

    # 1. DNS Lookup
    try:
        # Use the provided resolver to perform an A record lookup
        await resolver.resolve(domain, 'A')
    except Exception as e:
        result["message"] = f"Ошибка DNS-запроса: {e}"
        return result

    # 2. HTTP GET test
    status_code, _ = await http_get(f"http://{domain}", timeout=timeout)
    if status_code == 200:
        result["status"] = True
        result["message"] = "Домен доступен."
    else:
        result["message"] = f"Ошибка HTTP GET-запроса (статус: {status_code})."

    return result

async def check_service_connectivity(
    hostname: str,
    service_name: str,
    timeout: int,
    expected_keywords: list = None,
    blocked_keywords: list = None
) -> dict:
    """
    Checks service connectivity, including ping, HTTP content, and keywords.
    """
    result = {
        "status": False,
        "message": "",
        "ping_time": None,
        "advice": [],
        "inaccessible_domains": []
    }
    expected_keywords = expected_keywords or []
    blocked_keywords = blocked_keywords or []

    # 1. Ping test
    ping_success = False
    ping_result_ms = await ping_host(hostname)
    result["ping_time"] = ping_result_ms

    if ping_result_ms is None:
        result["message"] = "Хост недоступен (ошибка ping)."
        # Do NOT return here. Proceed to HTTP check.
    else:
        ping_success = True


    # 2. HTTP GET test
    status_code, content = await http_get(f"https://{hostname}", timeout=timeout)
    if status_code != 200:
        # Fallback to http if https fails
        status_code, content = await http_get(f"http://{hostname}", timeout=timeout)

    if status_code != 200:
        # If ping failed AND http failed
        if not ping_success:
            result["message"] = f"Хост недоступен (ошибка ping и HTTP/HTTPS статус: {status_code})."
        else: # Ping succeeded but HTTP failed
            result["message"] = f"Не удалось подключиться по HTTP/HTTPS (ping успешен, статус: {status_code})."
        result["inaccessible_domains"].append(hostname)
        return result

    # If HTTP GET was successful, clear any previous ping-related message if ping failed
    if not ping_success:
        result["message"] = "" # Clear message as HTTP succeeded

    # 3. Keyword checks
    for keyword in blocked_keywords:
        if keyword.lower() in content.lower():
            result["message"] = f"Найдено ключевое слово блокировки: '{keyword}'."
            result["advice"].append(f"Содержимое страницы похоже на страницу блокировки для сервиса {service_name}.")
            result["inaccessible_domains"].append(hostname)
            return result

    missing_keywords = []
    for keyword in expected_keywords:
        if keyword.lower() not in content.lower():
            missing_keywords.append(keyword)

    if missing_keywords:
        result["message"] = f"Ожидаемое содержимое не найдено. Отсутствует: {', '.join(missing_keywords)}."
        result["advice"].append("Содержимое страницы не соответствует ожидаемому для этого сервиса.")
        result["inaccessible_domains"].append(hostname)
        return result

    # If all checks pass
    result["status"] = True
    result["message"] = "Сервис доступен и содержимое соответствует ожиданиям."
    return result

async def run_command(command, timeout=10):
    try:
        proc = await asyncio.create_subprocess_shell(
            " ".join(command),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode == 0, stdout.decode()
    except (Exception, asyncio.TimeoutError):
        return False, ""

def command_exists(command):
    return subprocess.call(f"type {command}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def save_report(filepath: str, content: str) -> bool:
    """
    Saves the report content to a file.
    Creates the directory if it doesn't exist.
    """
    try:
        # Ensure the directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except (IOError, OSError) as e:
        # In a real app, we'd log this. For now, just returning False.
        return False

async def get_geo_ip_info(ip: str) -> dict:
    """
    Asynchronously gets Geo-IP information for a given IP address.
    """
    if not ip:
        return {"status": "fail", "message": "IP-адрес не предоставлен."}

    url = f"http://ip-api.com/json/{ip}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return {
                    "status": "success",
                    "country": data.get("country"),
                    "city": data.get("city"),
                    "isp": data.get("isp"),
                }
            else:
                return {"status": "fail", "message": data.get("message", "Ошибка запроса к API.")}
    except httpx.HTTPStatusError as e:
        return {"status": "fail", "message": f"Произошла ошибка HTTP: {e}"}
    except Exception as e:
        return {"status": "fail", "message": f"Произошла ошибка: {e}"}

async def ping_host(host: str, timeout: int = 2) -> float | None:
    """
    Pings a host and returns its latency in ms, or None if unreachable.
    """
    try:
        # -c 1: one packet
        # -W <timeout>: timeout in seconds
        command = ["ping", "-c", "1", "-W", str(timeout), host]
        ok, output = await run_command(command, timeout=timeout + 1)
        if ok:
            match = re.search(r"time=([\d\.]+)\s+ms", output)
            if match:
                return float(match.group(1))
        return None  # Return None if ping was not 'ok' or regex failed
    except Exception:
        return None

def now():
    return datetime.now()

def mask_ip(ip):
    return re.sub(r"\d", "x", ip)
