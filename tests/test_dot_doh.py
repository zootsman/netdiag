import asyncio
import pytest
from netdiag.modules.dns import check_dot, check_doh, resolver
from netdiag.logger import info

@pytest.mark.asyncio
async def test_dot_doh_checks():
    info("Запуск теста DoT/DoH проверок")
    # Используем известные публичные DNS-серверы, которые предположительно поддерживают DoT/DoH
    # Если системные DNS не обнаружены, resolver будет использовать 8.8.8.8 и 8.8.4.4
    dns_servers_to_test = resolver.nameservers if resolver.nameservers else ['8.8.8.8', '8.8.4.4']

    print(f"Тестирование DoT/DoH на серверах: {', '.join(dns_servers_to_test)}")

    for dns_ip in dns_servers_to_test:
        print(f"\nПроверка {dns_ip}:")
        dot_supported = await check_dot(dns_ip, timeout=5)
        doh_supported = await check_doh(dns_ip, timeout=5)

        print(f"  DoT поддерживается: {dot_supported}")
        print(f"  DoH поддерживается: {doh_supported}")

        # Мы не можем делать строгие утверждения, так как поддержка может меняться
        # и зависит от среды выполнения. Просто проверяем, что функции выполняются без ошибок.
        assert isinstance(dot_supported, bool)
        assert isinstance(doh_supported, bool)

    print("\nТест DoT/DoH проверок успешно пройден!")

if __name__ == "__main__":
    asyncio.run(test_dot_doh_checks())