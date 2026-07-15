"""
dns.py

Асинхронные функции для DNS запросов.
"""

import dns.asyncresolver
import dns.exception
import socket
import ssl
import asyncio
from ..logger import info, warning, error
from ..utils import get_system_dns_servers, http_get

# Инициализация асинхронного резолвера
resolver = dns.asyncresolver.Resolver(configure=False)

async def initialize_resolver(config: dict | None = None):
    """
    Асинхронно инициализирует и настраивает глобальный DNS-резолвер.
    """
    if config is None:
        config = {}
    
    try:
        system_dns = await get_system_dns_servers()
        if system_dns:
            resolver.nameservers = system_dns
            info(f"Использование системных DNS-серверов: {', '.join(system_dns)}")
        else:
            fallback_dns = config.get("fallback_dns", ['8.8.8.8', '8.8.4.4'])
            resolver.nameservers = fallback_dns
            warning(f"Системные DNS-серверы не найдены, используется fallback: {', '.join(fallback_dns)}")
    except Exception as e:
        fallback_dns = config.get("fallback_dns", ['8.8.8.8', '8.8.4.4'])
        resolver.nameservers = fallback_dns
        warning(f"Ошибка при получении системных DNS-серверов: {e}. Используется fallback: {', '.join(fallback_dns)}")


async def resolve_a_record(hostname: str) -> list[str]:
    """
    Асинхронно разрешает A-записи для данного имени хоста.
    """
    try:
        answers = await resolver.resolve(hostname, 'A')
        return [str(rdata) for rdata in answers]
    except dns.exception.DNSException as e:
        warning(f"Ошибка разрешения A-записи для {hostname}: {e}")
        return []

async def resolve_aaaa_record(hostname: str) -> list[str]:
    """
    Асинхронно разрешает AAAA-записи для данного имени хоста.
    """
    try:
        answers = await resolver.resolve(hostname, 'AAAA')
        return [str(rdata) for rdata in answers]
    except dns.exception.DNSException as e:
        warning(f"Ошибка разрешения AAAA-записи для {hostname}: {e}")
        return []

async def resolve_mx_record(hostname: str) -> list[str]:
    """
    Асинхронно разрешает MX-записи для данного имени хоста.
    """
    try:
        answers = await resolver.resolve(hostname, 'MX')
        return [f"{rdata.preference} {rdata.exchange}" for rdata in answers]
    except dns.exception.DNSException as e:
        warning(f"Ошибка разрешения MX-записи для {hostname}: {e}")
        return []

async def resolve_ns_record(hostname: str) -> list[str]:
    """
    Асинхронно разрешает NS-записи для данного имени хоста.
    """
    try:
        answers = await resolver.resolve(hostname, 'NS')
        return [str(rdata) for rdata in answers]
    except dns.exception.DNSException as e:
        warning(f"Ошибка разрешения NS-записи для {hostname}: {e}")
        return []

async def lookup_dns(hostname: str) -> dict[str, list[str]]:
    """
    Асинхронно выполняет все основные DNS запросы для данного имени хоста.
    """
    if not resolver.nameservers:
        await initialize_resolver()
    info(f"Выполнение асинхронного DNS запроса для: {hostname}")
    tasks = {
        "A": resolve_a_record(hostname),
        "AAAA": resolve_aaaa_record(hostname),
        "MX": resolve_mx_record(hostname),
        "NS": resolve_ns_record(hostname),
    }
    results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))

async def check_dot(hostname: str, ip_address: str, timeout: int = 5) -> bool:
    """
    Асинхронно проверяет, поддерживает ли DNS-сервер DNS over TLS (DoT) на порту 853.
    """
    info(f"Проверка DoT для {hostname} ({ip_address}) на порту 853 (таймаут: {timeout}s)")
    try:
        # Создаем SSL-контекст для проверки сертификата хоста
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                host=ip_address,
                port=853,
                ssl=ssl_context,
                server_hostname=hostname
            ),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        info(f"DoT поддерживается сервером {hostname}")
        return True
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError, ssl.SSLError, socket.gaierror) as e:
        warning(f"DoT не поддерживается или ошибка подключения к {hostname}: {e}")
        return False
    except Exception as e:
        error(f"Неизвестная ошибка при проверке DoT для {hostname}: {e}")
        return False


async def check_doh(url: str, timeout: int = 5) -> bool:
    """
    Асинхронно проверяет, поддерживает ли DNS-сервер DNS over HTTPS (DoH), отправляя запрос на заданный URL.
    """
    info(f"Проверка DoH для {url} (таймаут: {timeout}s)")
    try:
        # Для DoH достаточно успешного HTTP-статуса, так как мы не отправляем реальный DNS-запрос
        # Некоторые серверы могут возвращать 400 Bad Request на GET-запросы без ?dns=, но это все равно указывает на работающий эндпоинт
        status_code, _ = await http_get(url, timeout=timeout)
        if status_code and (200 <= status_code < 500): # Любой статус от 200 до 499 говорит о том, что сервер слушает
            info(f"DoH эндпоинт {url} активен (статус: {status_code}).")
            return True
        else:
            warning(f"DoH эндпоинт {url} не ответил ожидаемо (статус: {status_code}).")
            return False
    except Exception as e:
        error(f"Неизвестная ошибка при проверке DoH для {url}: {e}")
        return False