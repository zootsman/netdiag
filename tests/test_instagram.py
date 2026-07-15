import asyncio
import pytest
from netdiag.modules.instagram import run_instagram_checks
from netdiag.logger import info

@pytest.mark.asyncio
async def test_instagram_checks():
    info("Запуск теста проверок Instagram")
    results = await run_instagram_checks(timeout=10)

    assert "instagram_connectivity" in results
    assert isinstance(results["instagram_connectivity"]["status"], bool)

    print("Тест Instagram-проверок успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_instagram_checks())