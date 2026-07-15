import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "color": True,
    "timeout": 5,
    "cache_minutes": 10,
    "report": {
        "enabled": False,
        "format": "txt", # "json" or "txt"
        "filepath": "reports/netdiag_report_{timestamp}.txt"
    },
    "reputation": {
        "enabled": True,
        "provider": "ipinfo.io",
        "api_token": "YOUR_IPINFO_TOKEN"
    },
    "icmp_analysis": {
        "enabled": True,
        "ping_hosts": [
            "8.8.8.8",
            "1.1.1.1",
            "google.com"
        ],
        "traceroute_host": "google.com"
    },
    "tls_check": {
        "enabled": True,
        "check_hosts": [
            "google.com",
            "youtube.com",
            "github.com"
        ],
        "warn_days_before_expiry": 30
    },
    "mtu_check": {
        "enabled": True,
        "host": "8.8.8.8",
        "start_size": 1400,
        "end_size": 1500
    },
    "dot_doh_check": {
        "enabled": True,
        "servers": [
            {
                "name": "Google",
                "dot_host": "dns.google",
                "doh_url": "https://dns.google/dns-query",
                "ip": "8.8.8.8"
            },
            {
                "name": "Cloudflare",
                "dot_host": "cloudflare-dns.com",
                "doh_url": "https://cloudflare-dns.com/dns-query",
                "ip": "1.1.1.1"
            },
            {
                "name": "Quad9",
                "dot_host": "dns.quad9.net",
                "doh_url": "https://dns.quad9.net/dns-query",
                "ip": "9.9.9.9"
            },
            {
                "name": "AdGuard",
                "dot_host": "dns.adguard-dns.com",
                "doh_url": "https://dns.adguard-dns.com/dns-query",
                "ip": "94.140.14.14"
            }
        ]
    },
    "services": [
        # ... existing services ...
    ],
    "port_scan": {
        "enabled": False,
        "hosts": [],
        "default_ports": [80, 443, 22],
        "timeout_per_port": 1
    }
}


def load_config():
    CONFIG_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            loaded_cfg = json.load(f)
        # Объединяем загруженную конфигурацию с конфигурацией по умолчанию
        # Это позволяет добавлять новые ключи по умолчанию, сохраняя пользовательские настройки
        merged_cfg = DEFAULT_CONFIG.copy()
        merged_cfg.update(loaded_cfg)
        return merged_cfg
    except Exception:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(cfg):
    CONFIG_DIR.mkdir(exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)