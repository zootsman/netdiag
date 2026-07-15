import asyncio
import pytest
from netdiag.modules.chatgpt import run_chatgpt_checks
from netdiag.logger import info

@pytest.mark.asyncio
async def test_chatgpt_checks():
    info("Запуск теста проверок ChatGPT")
    results = await run_chatgpt_checks(timeout=10)

    assert "chatgpt_connectivity" in results
    assert isinstance(results["chatgpt_connectivity"]["status"], bool)

    print("Тест ChatGPT-проверок успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_chatgpt_checks())