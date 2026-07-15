import asyncio
import pytest
from netdiag.modules.dns import lookup_dns
from netdiag.logger import info

@pytest.mark.asyncio
async def test_dns_lookup():
    info("Запуск теста DNS запроса для google.com")
    results = await lookup_dns("google.com")

    assert "A" in results
    assert "AAAA" in results
    assert "MX" in results
    assert "NS" in results

    assert len(results["A"]) > 0, "Должны быть A записи для google.com"
    assert len(results["AAAA"]) > 0, "Должны быть AAAA записи для google.com"
    assert len(results["MX"]) > 0, "Должны быть MX записи для google.com"
    assert len(results["NS"]) > 0, "Должны быть NS записи для google.com"

    print("Тест DNS запроса успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_dns_lookup())