import re
import asyncio
import httpx
from rich.console import Console

# --- Mock Data and Configuration (Simplified from config.default.json) ---
MOCK_SERVICE_CONFIGS = {
    "google": {
        "main_hostname": "www.google.com",
        "content_country_indicators": {
            "regex": [
                r"window\.location\.href\s*=\s*['"].*?google\.([a-z]{2})",
                r"hl=([a-z]{2})"
            ],
            "strings": {
                "US": ["United States", "English (United States)"],
                "RU": ["Россия", "русский"],
                "DE": ["Deutschland", "Deutsch"],
                "FR": ["France", "Français"],
            }
        }
    },
    "youtube": {
        "main_hostname": "www.youtube.com",
        "content_country_indicators": {
            "regex": [
                r""INNERTUBE_CONTEXT_WEB_CLIENT_INFO":.*?"gl":"([A-Z]{2})""
            ],
            "strings": {
                "US": ["United States"],
                "RU": ["Россия", "YouTube Россия"],
                "DE": ["Deutschland"],
            }
        }
    },
    "instagram": {
        "main_hostname": "www.instagram.com",
        "content_country_indicators": {
            "regex": [
                r""country_code":"([A-Z]{2})""
            ],
            "strings": {
                "US": ["English (US)"],
                "RU": ["Русский", "Instagram Россия"],
                "DE": ["Deutsch"],
            }
        }
    }
}

# --- Core Logic for Country Extraction ---
async def extract_country_from_content(content: str, indicators: dict) -> str | None:
    """
    Extracts a country code (ISO 2-letter) from content using defined indicators.
    """
    content_lower = content.lower()

    # 1. Check regex patterns
    if indicators.get("regex"):
        for pattern in indicators["regex"]:
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                extracted_code = match.group(1).upper()
                if extracted_code == "EN": # Specific handling for Google's 'en' language code
                    return "US"
                return extracted_code

    # 2. Check specific strings
    if indicators.get("strings"):
        for country_code, country_strings in indicators["strings"].items():
            for s in country_strings:
                if s.lower() in content_lower:
                    return country_code.upper()

    return None

# --- Simulated check_service_connectivity with live HTTP requests ---
async def check_service_connectivity_simulated(
    hostname: str,
    timeout: int,
    content_country_indicators: dict
) -> dict:
    """
    Simulates the service connectivity check, including live HTTP GET and country extraction.
    """
    result = {
        "status": False,
        "message": "",
        "service_perceived_country": None,
        "raw_content_snippet": "" # For debugging/demonstration
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(f"https://{hostname}", timeout=timeout)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
            content = response.text
            result["raw_content_snippet"] = content[:500] + "..." if len(content) > 500 else content

            # Extract country from content
            service_country = await extract_country_from_content(content, content_country_indicators)
            result["service_perceived_country"] = service_country
            
            result["status"] = True
            result["message"] = "Сервис доступен."

    except httpx.RequestError as e:
        result["message"] = f"Ошибка запроса к {hostname}: {e}"
    except httpx.HTTPStatusError as e:
        result["message"] = f"Ошибка HTTP от {hostname}: {e.response.status_code}"
    except Exception as e:
        result["message"] = f"Неожиданная ошибка для {hostname}: {e}"

    return result

# --- Main demonstration runner ---
async def run_live_geo_demo():
    console = Console()
    console.print("[bold blue]--- Запуск демонстрации проверки географического соответствия сервисов (Live) ---[/bold blue]")

    # Mock agent's country (from GeoIP) - this would come from the network plugin in real app
    agent_country = "DE" # Let's assume our agent is in Germany for this demo

    for service_name, config in MOCK_SERVICE_CONFIGS.items():
        console.print(f"[bold magenta]Проверка сервиса: {service_name.capitalize()}[/bold magenta]")
        
        simulated_check_result = await check_service_connectivity_simulated(
            hostname=config["main_hostname"],
            timeout=10,
            content_country_indicators=config["content_country_indicators"]
        )

        console.print(f"  [cyan]Статус:[/cyan] {simulated_check_result['message']}")
        console.print(f"  [cyan]Ваша страна (GeoIP):[/cyan] [green]{agent_country}[/green]")
        console.print(f"  [cyan]Страна, воспринимаемая сервисом:[/cyan] [yellow]{simulated_check_result['service_perceived_country'] or 'Не определено'}[/yellow]")
        
        if simulated_check_result["status"] and simulated_check_result["service_perceived_country"]:
            if simulated_check_result["service_perceived_country"] != agent_country:
                console.print(f"  [red]❗ Несоответствие: Сервис {service_name.capitalize()} видит вас в стране '{simulated_check_result['service_perceived_country']}', хотя ваш IP из '{agent_country}'.[/red]")
            else:
                console.print(f"  [green]✔ Соответствие: Сервис {service_name.capitalize()} видит вас в '{agent_country}'.[/green]")
        elif not simulated_check_result["status"]:
            console.print(f"  [red]Проверка сервиса {service_name.capitalize()} завершилась неудачей.[/red]")
        else:
            console.print(f"  [yellow]Предупреждение: Не удалось определить страну, воспринимаемую сервисом {service_name.capitalize()}.[/yellow]")
        
        # Optional: Print a snippet of raw content for deeper inspection
        # console.print(f"  [dim]Фрагмент содержимого:[/dim]
[dim]{simulated_check_result['raw_content_snippet']}[/dim]")

if __name__ == "__main__":
    asyncio.run(run_live_geo_demo())