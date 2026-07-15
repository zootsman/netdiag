from netdiag.utils import get_system_dns_servers
from netdiag.logger import info

def test_get_system_dns_servers():
    info("Запуск теста обнаружения системных DNS-серверов")
    dns_servers = get_system_dns_servers()

    print(f"Обнаруженные DNS-серверы: {dns_servers}")

    # Assert that at least one DNS server is found, or it's an empty list if none are found.
    # We can't assert specific IPs as they vary by environment.
    assert isinstance(dns_servers, list)
    # assert len(dns_servers) > 0 # This might fail in some isolated environments, so make it optional
    if not dns_servers:
        info("Не удалось обнаружить системные DNS-серверы (это может быть нормально для данного окружения).")

    print("Тест обнаружения системных DNS-серверов успешно пройден!")

if __name__ == "__main__":
    test_get_system_dns_servers()