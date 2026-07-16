import re
import asyncio
import httpx # For simulating http_get if needed, or just mock content
from rich.console import Console # Import Console from rich

# --- Mock Data and Configuration (Simplified from config.default.json) ---
MOCK_SERVICE_CONFIGS = {
    "google": {
        "main_hostname": "www.google.com",
        "content_country_indicators": {
            "regex": [ # Regex patterns to extract country code (e.g., from URL or specific tags)
                r"window\.location\.href\s*=\s*['\"].*?google\.([a-z]{2})", # google.fr, google.de
                r"hl=([a-z]{2})" # language parameter
            ],
            "strings": { # Keywords indicating country, mapped to country codes
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
                r"\"INNERTUBE_CONTEXT_WEB_CLIENT_INFO\":.*?\"gl\":\"([A-Z]{2})\"" # YouTube's country code in JS context
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
                r"\"country_code\":\"([A-Z]{2})\"" # Instagram's country code in JS context
            ],
            "strings": {
                "US": ["English (US)"],
                "RU": ["Русский", "Instagram Россия"],
                "DE": ["Deutsch"],
            }
        }
    }
}

# --- Core Logic for Country Extraction (to be similar to check_service_connectivity in utils.py) ---
async def extract_country_from_content(content: str, indicators: dict) -> str | None:
    """
    Extracts a country code (ISO 2-letter) from content using defined indicators.
    """
    content_lower = content.lower()

    # 1. Check regex patterns
    if indicators.get("regex"):
        for pattern in indicators["regex"]:
            match = re.search(pattern, content_lower, re.IGNORECASE) # Add re.IGNORECASE flag
            if match:
                extracted_code = match.group(1).upper()
                # Special handling for language codes that imply a country for Google
                if extracted_code == "EN":
                    return "US" # Assuming 'en' typically means US for Google context
                return extracted_code

    # 2. Check specific strings
    if indicators.get("strings"):
        for country_code, country_strings in indicators["strings"].items():
            for s in country_strings:
                if s.lower() in content_lower:
                    return country_code.upper()

    return None

# --- Mock HTML Content for Testing ---
MOCK_HTML_CONTENT = {
    "google_us": """
        <html><body><p>Welcome to Google United States</p><a href="https://www.google.com/search?q=test&hl=en-US">Search</a></body></html>
    """,
    "google_ru": """
        <html><body><p>Добро пожаловать в Google Россия</p><a href="https://www.google.ru/search?q=test&hl=ru">Поиск</a></body></html>
    """,
    "google_de": """
        <html><body><p>Willkommen bei Google Deutschland</p><a href="https://www.google.de/search?q=test&hl=de">Suchen</a></body></html>
    """,
    "youtube_us": """
        <script>var data = {"INNERTUBE_CONTEXT_WEB_CLIENT_INFO": {"gl":"US"}};</script>
        <body>Welcome to YouTube United States</body>
    """,
    "youtube_ru": """
        <script>var data = {"INNERTUBE_CONTEXT_WEB_CLIENT_INFO": {"gl":"RU"}};</script>
        <body>Добро пожаловать в YouTube Россия</body>
    """,
    "instagram_us": """
        <script>var config = {"country_code":"US"};</script>
        <body>Welcome to Instagram</body>
    """,
    "instagram_de": """
        <script>var config = {"country_code":"DE"};</script>
        <body>Willkommen bei Instagram Deutschland</body>
    """,
    "instagram_no_geo": """
        <html><body><h1>Instagram</h1></body></html>
    """
}

# --- Test Runner ---
async def run_geo_tests():
    console = Console() # Initialize Console here
    # print("--- Запуск тестов географического соответствия сервисов ---") # Removed debug print

    test_cases = [
        ("google", MOCK_HTML_CONTENT["google_us"], "US"),
        ("google", MOCK_HTML_CONTENT["google_ru"], "RU"),
        ("google", MOCK_HTML_CONTENT["google_de"], "DE"),
        ("youtube", MOCK_HTML_CONTENT["youtube_us"], "US"),
        ("youtube", MOCK_HTML_CONTENT["youtube_ru"], "RU"),
        ("instagram", MOCK_HTML_CONTENT["instagram_us"], "US"),
        ("instagram", MOCK_HTML_CONTENT["instagram_de"], "DE"),
        ("instagram", MOCK_HTML_CONTENT["instagram_no_geo"], None), # Expect None if no country found
    ]

    for service_name, html_content, expected_country in test_cases:
        indicators = MOCK_SERVICE_CONFIGS[service_name]["content_country_indicators"]
        detected_country = await extract_country_from_content(html_content, indicators)
        
        status_text = "[green]✔ ПРОЙДЕНО[/green]" if detected_country == expected_country else f"[red]✘ НЕУДАЧА (ожидалось: {expected_country}, получено: {detected_country})[/red]"
        console.print(f"Тест для {service_name} (HTML: {list(MOCK_HTML_CONTENT.keys())[list(MOCK_HTML_CONTENT.values()).index(html_content)]}): {status_text}")

if __name__ == "__main__":
    asyncio.run(run_geo_tests())