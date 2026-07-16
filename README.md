# NetDiag: Утилита для диагностики сети

`NetDiag` — это мощная и гибкая утилита для комплексной диагностики сетевых проблем. Она позволяет выполнять различные сетевые проверки, анализировать их результаты и представлять информацию в удобном формате. Благодаря модульной архитектуре на основе плагинов, `NetDiag` легко расширяется и настраивается под ваши нужды.

## Основные возможности

*   **Проверка зависимостей:** Автоматически определяет наличие необходимых системных утилит (например, `ping`, `traceroute`) и Python-модулей.
*   **Анализ сети:** Определяет публичный IP-адрес, географическое местоположение и провайдера.
*   **Репутация IP:** Проверяет репутацию вашего IP-адреса с использованием внешних сервисов (с учетом лимитов API).
*   **DNS Запросы:** Выполняет DNS-запросы (A, AAAA, MX, NS записи) для указанных доменов.
*   **DoT/DoH Проверки:** Тестирует доступность и работоспособность защищенных DNS-серверов (DNS-over-TLS и DNS-over-HTTPS).
*   **ICMP Анализ:** Выполняет пинг до целевых хостов и трассировку маршрута для определения сетевых задержек и узких мест.
*   **SSL/TLS Проверки:** Анализирует SSL/TLS сертификаты для указанных хостов, проверяя их валидность и срок действия.
*   **Определение MTU:** Помогает найти оптимальный размер MTU для вашего сетевого соединения.
*   **Проверки Сервисов:** Тестирует доступность и ожидаемое содержимое внешних веб-сервисов (например, Google, YouTube, Telegram, GitHub).
*   **Бенчмарк DNS-резолверов:** Сравнивает производительность различных публичных DNS-серверов для выбора оптимального.
*   **Сканирование портов:** Определяет открытые и закрытые порты на указанных хостах. Результаты выводятся в удобной табличной форме.
*   **Гибкая конфигурация:** Все проверки и их параметры настраиваются через конфигурационные файлы (JSON).
*   **Отчетность:** Результаты всех проверок могут быть сохранены в различных форматах (JSON, текстовый файл).

## Запуск NetDiag

`NetDiag` поддерживает запуск всех или отдельных проверок через аргументы командной строки, а также интерактивный режим.

### 1. Локальная установка (рекомендуемый способ)

Для использования `NetDiag` рекомендуется клонировать репозиторий и установить зависимости в виртуальное окружение.

**Требования:** `git`, `python3`, `python3-venv` (может потребоваться установка системного пакета).

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/zootsman/netdiag.git
    cd netdiag
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Запуск программы:**

    *   **Интерактивное меню:**
        Если запустить `netdiag.py` без аргументов, будет показано интерактивное меню, где вы сможете выбрать нужные проверки.
        ```bash
        python netdiag.py
        ```

    *   **Запуск всех проверок:**
        Используйте флаг `--all` для выполнения всех доступных диагностических проверок.
        ```bash
        python netdiag.py --all
        ```

    *   **Запуск отдельных проверок:**
        Вы можете указать одну или несколько проверок, используя соответствующие флаги. Например, для запуска только сканирования портов и DNS-бенчмарка:
        ```bash
        python netdiag.py --port_scan --dns_benchmark
        ```
        Доступные флаги для проверок (соответствуют названиям плагинов):
        *   `--network`: Анализ сети и репутации IP
        *   `--dns`: DNS Запрос
        *   `--dot_doh`: Проверка DoT/DoH
        *   `--icmp`: Анализ ICMP (Ping, Traceroute)
        *   `--tls`: Проверка SSL/TLS Сертификатов
        *   `--mtu`: Определение MTU
        *   `--services`: Проверки Сервисов
        *   `--dns_benchmark`: Бенчмарк DNS-резолверов
        *   `--port_scan`: Сканирование портов

### 2. Запуск из исходного кода (без установки, только для разработчиков)
Данный метод подходит для быстрого тестирования или разработки.

**Требования:** `git`, `python3`, `pip`.

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/zootsman/netdiag.git
    cd netdiag
    ```

2.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Запуск программы:**
    *   **Интерактивное меню:**
        ```bash
        python netdiag.py
        ```
    *   **Запуск всех проверок:**
        ```bash
        python netdiag.py --all
        ```

---
---

# NetDiag: A Network Diagnostic Utility

`NetDiag` is a powerful and flexible utility for comprehensive diagnosis of network problems. It allows you to perform various network checks, analyze their results, and present information in a user-friendly format. Thanks to its modular, plugin-based architecture, `NetDiag` is easily extensible and customizable to your needs.

## Key Features

*   **Dependency Check:** Automatically identifies the presence of necessary system utilities (e.g., `ping`, `traceroute`) and Python modules.
*   **Network Analysis:** Determines public IP address, geographic location, and provider.
*   **IP Reputation:** Checks the reputation of your IP address using external services (considering API limits).
*   **DNS Queries:** Performs DNS queries (A, AAAA, MX, NS records) for specified domains.
*   **DoT/DoH Checks:** Tests the availability and functionality of secure DNS servers (DNS-over-TLS and DNS-over-HTTPS).
*   **ICMP Analysis:** Performs ping to target hosts and traceroute to determine network latencies and bottlenecks.
*   **SSL/TLS Checks:** Analyzes SSL/TLS certificates for specified hosts, verifying their validity and expiration.
*   **MTU Discovery:** Helps find the optimal MTU size for your network connection.
*   **Service Checks:** Tests the availability and expected content of external web services (e.g., Google, YouTube, Telegram, GitHub).
*   **DNS Resolver Benchmark:** Compares the performance of various public DNS resolvers to choose the optimal one.
*   **Port Scanning:** Identifies open and closed ports on specified hosts. Results are displayed in a convenient table format.
*   **Flexible Configuration:** All checks and their parameters are configurable via JSON files.
*   **Reporting:** Results of all checks can be saved in various formats (JSON, text file).

## Running NetDiag

`NetDiag` supports running all or individual checks via command-line arguments, as well as an interactive mode.

### 1. Local Installation (Recommended)

For using `NetDiag`, it is recommended to clone the repository and install dependencies in a virtual environment.

**Requirements:** `git`, `python3`, `python3-venv` (system package might be required).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/zootsman/netdiag.git
    cd netdiag
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the program:**

    *   **Interactive menu:**
        If you run `netdiag.py` without arguments, an interactive menu will be displayed where you can select the desired checks.
        ```bash
        python netdiag.py
        ```

    *   **Run all checks:**
        Use the `--all` flag to perform all available diagnostic checks.
        ```bash
        python netdiag.py --all
        ```

    *   **Run individual checks:**
        You can specify one or more checks using the corresponding flags. For example, to run only port scanning and DNS benchmark:
        ```bash
        python netdiag.py --port_scan --dns_benchmark
        ```
        Available flags for checks (correspond to plugin names):
        *   `--network`: Network and IP Reputation Analysis
        *   `--dns`: DNS Query
        *   `--dot_doh`: DoT/DoH Check
        *   `--icmp`: ICMP Analysis (Ping, Traceroute)
        *   `--tls`: SSL/TLS Certificate Check
        *   `--mtu`: MTU Discovery
        *   `--services`: Service Checks
        *   `--dns_benchmark`: DNS Resolver Benchmark
        *   `--port_scan`: Port Scanning

### 2. Running from Source (Developers Only)
This method is suitable for quick testing or development.

**Requirements:** `git`, `python3`, `pip`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/zootsman/netdiag.git
    cd netdiag
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the program:**
    *   **Interactive menu:**
        ```bash
        python netdiag.py
        ```
    *   **Run all checks:**
        ```bash
        python netdiag.py --all
        ```
