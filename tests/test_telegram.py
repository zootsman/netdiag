import asyncio
import pytest
from netdiag.modules.telegram import run_telegram_checks
from netdiag.logger import info

@pytest.mark.asyncio
async def test_telegram_checks():
    info("Запуск теста проверок Telegram")
    results = await run_telegram_checks(timeout=10)

    assert "telegram_connectivity" in results
    assert isinstance(results["telegram_connectivity"]["status"], bool)

    print("Тест Telegram-проверок успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_telegram_checks())