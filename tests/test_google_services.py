import asyncio
import pytest
from netdiag.modules.google import run_google_checks
from netdiag.logger import info

@pytest.mark.asyncio
async def test_google_services_checks():
    info("Запуск теста проверок Google-сервисов")
    results = await run_google_checks(timeout=10)

    assert "google_connectivity" in results
    assert "youtube_connectivity" in results

    assert isinstance(results["google_connectivity"]["status"], bool)
    assert isinstance(results["youtube_connectivity"]["status"], bool)

    print("Тест Google-сервисов успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_google_services_checks())