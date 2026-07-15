import asyncio
import pytest
from netdiag.modules.google import run_google_checks
from netdiag.logger import info

@pytest.mark.asyncio
async def test_google_checks():
    info("Запуск теста Google-проверок")
    results = await run_google_checks(timeout=10) # Use a slightly longer timeout for external calls

    assert "connectivity" in results
    assert results["connectivity"] is True, "Должно быть подключение к www.google.com"

    print("Тест Google-проверок успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_google_checks())