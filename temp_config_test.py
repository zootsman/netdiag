import re

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

print(MOCK_SERVICE_CONFIGS)
