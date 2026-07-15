import asyncio
import pytest
from netdiag.modules.gemini import run_gemini_checks
from netdiag.logger import info

@pytest.mark.asyncio
async def test_gemini_checks():
    info("Запуск теста проверок Google Gemini")
    results = await run_gemini_checks(timeout=10)

    assert "gemini_connectivity" in results
    assert isinstance(results["gemini_connectivity"]["status"], bool)

    print("Тест Google Gemini-проверок успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_gemini_checks())