"""
logger.py

Логирование NetDiag.
"""

from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "netdiag.log"


def log(level: str, message: str) -> None:
    """
    Записать сообщение в журнал.
    """

    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] [{level}] {message}\\n")


def info(message: str) -> None:
    log("INFO", message)


def warning(message: str) -> None:
    log("WARNING", message)


def error(message: str) -> None:
    log("ERROR", message)