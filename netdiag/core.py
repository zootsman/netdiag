from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json

from .version import get_version
from .dependency import check_dependencies
from .config import load_config
from .modules.network import get_public_ip
from .modules.reputation import check_ip_reputation
from .modules.icmp import run_icmp_analysis
from .modules.tls import run_tls_analysis
from .modules.mtu import run_mtu_check
from .modules.dns import lookup_dns, resolver, check_dot, check_doh, initialize_resolver
from .modules.dns_benchmark import run_dns_benchmark
from .modules.port_scan import run_port_scan
from .modules.cdn import check_cdn_info # New import
from .utils import get_geo_ip_info, save_report, now, check_service_connectivity, check_domain_reachability

console = Console()

async def check_dependencies_and_report(report_data):
    """Checks for missing dependencies and updates the report data."""
    console.print("\n[bold cyan]Проверка зависимостей[/bold cyan]")
    missing = check_dependencies(console)
    if missing:
        console.print("\n[red]Отсутствуют зависимости:[/red]")
        report_data["dependencies"] = {"status": "missing", "missing": missing}
        for pkg in missing:
            console.print(f" • {pkg}")
        return False
    else:
        console.print("[green]✔ Все зависимости установлены.[/green]")
        report_data["dependencies"] = {"status": "ok"}
        return True

async def perform_network_analysis(report_data, cfg):
    """Gets public IP, GeoIP info, and IP reputation."""
    console.print("\n[bold cyan]Анализ сети и репутации IP[/bold cyan]")
    report_data["network"] = {}
    ip = await get_public_ip(cfg["timeout"])
    report_data["network"]["public_ip"] = ip if ip else "N/A"

    if not ip:
        console.print("[red]Не удалось определить публичный IP[/red]")
        return

    console.print(f"[green]Публичный IPv4:[/green] {ip}")
    
    # Geo-IP Info
    geo_info = await get_geo_ip_info(ip)
    report_data["network"]["geo_ip"] = geo_info
    if geo_info.get("status") == "success":
        country = geo_info.get("country", "N/A")
        city = geo_info.get("city", "N/A")
        isp = geo_info.get("isp", "N/A")
        console.print(f"[green]Местоположение:[/green] {city}, {country}")
        console.print(f"[green]Провайдер:[/green] {isp}")
    else:
        console.print("[yellow]Не удалось определить Geo-IP информацию.[/yellow]")

    # IP Reputation Check
    reputation_info = await check_ip_reputation(ip, cfg)
    report_data["network"]["reputation"] = reputation_info
    
    if not reputation_info["check_enabled"]:
        console.print(f"[yellow]{reputation_info['message']}[/yellow]")
    elif reputation_info["is_privacy_risk"]:
        console.print(f"[red]❗ {reputation_info['message']}[/red]")
        for provider_data in reputation_info["providers_data"]:
            if provider_data.get("vpn") or provider_data.get("proxy") or provider_data.get("tor") or provider_data.get("hosting"):
                issues = []
                if provider_data.get("vpn"): issues.append("VPN")
                if provider_data.get("proxy"): issues.append("Прокси")
                if provider_data.get("tor"): issues.append("Tor")
                if provider_data.get("hosting"): issues.append("Хостинг")
                console.print(f"  [red]  • {provider_data['provider']}: Обнаружено: {', '.join(issues)} ({provider_data.get('message', 'Нет подробностей')})[/red]")
            elif "Ошибка" in provider_data.get("message", ""):
                 console.print(f"  [yellow]  • {provider_data['provider']}: {provider_data['message']}[/yellow]")
    else:
        console.print(f"[green]✔ {reputation_info['message']}[/green]")
    
    # CDN Check
    cdn_info = await check_cdn_info(ip, cfg["timeout"])
    report_data["network"]["cdn"] = cdn_info
    if cdn_info["cdn_detected"]:
        console.print(f"[green]✔ CDN Обнаружен:[/green] {cdn_info['provider']}")
        if cdn_info["edge_location"]:
            console.print(f"[green]  Edge Location:[/green] {cdn_info['edge_location']}")
        if cdn_info["country"]:
            console.print(f"[green]  Страна CDN:[/green] {cdn_info['country']}")
    else:
        console.print(f"[yellow]{cdn_info['message']}[/yellow]")

async def perform_dns_lookup(report_data):
    """Performs a DNS lookup for google.com."""
    console.print("\n[bold cyan]DNS Запрос (google.com)[/bold cyan]")
    dns_results = await lookup_dns("google.com")
    report_data["dns"]["google_com_lookup"] = dns_results

    for record_type, records in dns_results.items():
        if records:
            console.print(f"[green]{record_type} записи:[/green]")
            for record in records:
                console.print(f" • {record}")
        else:
            console.print(f"[yellow]Нет {record_type} записей или ошибка.[/yellow]")

async def perform_dot_doh_check(report_data, cfg):
    """Проверяет поддержку DoT/DoH на предварительно настроенных публичных DNS-серверах."""
    console.print("\n[bold cyan]Проверка доступности публичных DoT/DoH серверов[/bold cyan]")
    
    check_cfg = cfg.get("dot_doh_check", {})
    if not check_cfg.get("enabled"):
        console.print("[yellow]Проверка DoT/DoH отключена в конфигурации.[/yellow]")
        report_data["dns"]["dot_doh_checks"] = {"status": "disabled"}
        return

    servers_to_check = check_cfg.get("servers", [])
    if not servers_to_check:
        console.print("[yellow]Нет серверов для проверки DoT/DoH в конфигурации.[/yellow]")
        report_data["dns"]["dot_doh_checks"] = {"status": "no_servers_configured"}
        return

    report_data["dns"]["dot_doh_checks"] = {}
    timeout = cfg.get("timeout", 5)
    overall_failure = False

    for server in servers_to_check:
        server_name = server.get("name", "N/A")
        console.print(f"\n[bold magenta]Проверка сервера: {server_name}[/bold magenta]")
        report_data["dns"]["dot_doh_checks"][server_name] = {}

        # Проверка DoT
        dot_host = server.get("dot_host")
        dot_ip = server.get("ip")
        if dot_host and dot_ip:
            dot_supported = await check_dot(dot_host, dot_ip, timeout)
            report_data["dns"]["dot_doh_checks"][server_name]["dot"] = dot_supported
            if dot_supported:
                console.print(f"[green]✔ DoT ({dot_host}) поддерживается[/green]")
            else:
                console.print(f"[red]✘ DoT ({dot_host}) не поддерживается или заблокирован[/red]")
                overall_failure = True
        else:
            report_data["dns"]["dot_doh_checks"][server_name]["dot"] = "not_configured"

        # Проверка DoH
        doh_url = server.get("doh_url")
        if doh_url:
            doh_supported = await check_doh(doh_url, timeout)
            report_data["dns"]["dot_doh_checks"][server_name]["doh"] = doh_supported
            if doh_supported:
                console.print(f"[green]✔ DoH ({doh_url}) поддерживается[/green]")
            else:
                console.print(f"[red]✘ DoH ({doh_url}) не поддерживается или заблокирован[/red]")
                overall_failure = True
        else:
            report_data["dns"]["dot_doh_checks"][server_name]["doh"] = "not_configured"

    if overall_failure:
        console.print("\n[bold yellow]Обнаружены проблемы с доступностью защищенных DNS-серверов.[/bold yellow]")
        console.print("  [bold]Объяснение:[/bold] Протоколы DNS-over-TLS (DoT) и DNS-over-HTTPS (DoH) шифруют ваши DNS-запросы,")
        console.print("  повышая приватность и безопасность. Если эти серверы недоступны, это может быть признаком")
        console.print("  блокировки со стороны вашего интернет-провайдера (ISP) или сетевого экрана.")
        console.print("  [bold]Рекомендации:[/bold]")
        console.print("  • Попробуйте использовать VPN для обхода возможных блокировок.")
        console.print("  • Проверьте настройки вашего роутера или файервола на предмет блокировки портов 853 (DoT) или 443 (DoH).")
        console.print("  • Вы можете настроить системный DNS на один из работающих серверов, если таковые имеются.")

async def perform_icmp_analysis(report_data, cfg):
    """Runs ICMP analysis and displays results."""
    console.print("\n[bold cyan]Анализ ICMP (Ping и Traceroute)[/bold cyan]")
    icmp_results = await run_icmp_analysis(cfg)
    report_data["icmp_analysis"] = icmp_results
    
    if not icmp_results.get("check_enabled"):
        console.print("[yellow]Проверка отключена в конфигурации.[/yellow]")
        return

    ping_failures = 0
    for host, result in icmp_results.get("ping_results", {}).items():
        if result["status"] == "ok":
            console.print(f"[green]✔ Ping {host}:[/green] {result['avg_latency_ms']:.2f} мс")
        else:
            console.print(f"[red]✘ Ping {host}:[/red] {result['error']}")
            ping_failures += 1
            
    if ping_failures > 0:
        console.print("\n[bold yellow]Обнаружены проблемы с ICMP (Ping).[/bold yellow]")
        console.print("  [bold]Объяснение:[/bold] Утилита ping отправляет ICMP-пакеты для проверки доступности хоста.")
        console.print("  Неудачные попытки могут означать, что хост выключен, недоступен из вашей сети, или что")
        console.print("  ICMP-трафик (используемый для ping) блокируется файерволом на пути к хосту или на самом хосте.")
        console.print("  [bold]Рекомендации:[/bold]")
        console.print("  • Убедитесь, что имя хоста написано правильно.")
        console.print("  • Попробуйте пинговать другие хосты, чтобы определить, является ли проблема специфичной для одного адреса.")
        console.print("  • Если все пинги не удаются, проверьте ваше интернет-соединение и настройки локального файервола.")

    traceroute_result = icmp_results.get("traceroute_result", {})
    if traceroute_result:
        console.print(f"\n[bold]Traceroute до {traceroute_result.get('host')}:[/bold]")
        if traceroute_result["status"] == "ok":
            console.print(f"[dim]{traceroute_result['output']}[/dim]")
        else:
            console.print(f"[red]Ошибка: {traceroute_result['output']}[/red]")

async def perform_tls_analysis(report_data, cfg):
    """Runs TLS analysis and displays results."""
    console.print("\n[bold cyan]Проверка SSL/TLS Сертификатов[/bold cyan]")
    tls_results = await run_tls_analysis(cfg)
    report_data["tls_analysis"] = tls_results

    if not tls_results.get("check_enabled"):
        console.print("[yellow]Проверка отключена в конфигурации.[/yellow]")
        return

    warn_days = cfg.get("tls_check", {}).get("warn_days_before_expiry", 30)
    tls_errors = 0
    for host, result in tls_results.get("hosts", {}).items():
        console.print(f"\n[bold magenta]Сертификат для {host}[/bold magenta]")
        if result["status"] == "ok":
            console.print(f"  [green]Выдан:[/green] {result['issuer']}")
            console.print(f"  [green]Субъект:[/green] {result['subject']}")
            
            expiry_date = result['expires']
            if expiry_date:
                console.print(f"  [green]Истекает:[/green] {expiry_date.strftime('%Y-%m-%d')}")
                days_left = (expiry_date - datetime.now()).days
                if days_left < 0:
                    console.print(f"  [bold red]❗ СЕРТИФИКАТ ИСТЕК {abs(days_left)} дней назад[/bold red]")
                    tls_errors += 1
                elif days_left < warn_days:
                    console.print(f"  [bold yellow]⚠ Истекает через {days_left} дней[/bold yellow]")
            else:
                console.print("  [yellow]Не удалось определить дату истечения.[/yellow]")
        else:
            console.print(f"  [red]Ошибка: {result['error']}[/red]")
            tls_errors += 1
            
    if tls_errors > 0:
        console.print("\n[bold red]Обнаружены серьезные проблемы с SSL/TLS сертификатами![/bold red]")
        console.print("  [bold]Объяснение:[/bold] SSL/TLS сертификаты используются для шифрования трафика и подтверждения подлинности сайтов.")
        console.print("  Ошибки (истекший срок действия, неверное имя хоста, недоверенный издатель) могут указывать на попытку")
        console.print("  перехвата вашего трафика (атака 'человек-по-середине', Man-in-the-Middle).")
        console.print("  [bold]Рекомендации:[/bold]")
        console.print("  • [bold red]КРАЙНЕ НЕ РЕКОМЕНДУЕТСЯ[/bold red] передавать чувствительные данные (пароли, номера карт) сайтам с ошибками сертификатов.")
        console.print("  • Проблема может быть на стороне сервера. Если вы не доверяете сети, воздержитесь от использования ресурса.")
        console.print("  • Убедитесь, что системное время на вашем устройстве настроено правильно, так как это влияет на проверку сертификатов.")

async def perform_mtu_check(report_data, cfg):
    """Runs MTU check and displays results."""
    console.print("\n[bold cyan]Определение MTU[/bold cyan]")
    mtu_results = await run_mtu_check(cfg)
    report_data["mtu_discovery"] = mtu_results

    if not mtu_results.get("check_enabled"):
        console.print("[yellow]Проверка отключена в конфигурации.[/yellow]")
        return
        
    if mtu_results.get("found_mtu"):
        console.print(f"[green]✔ Оптимальный MTU:[/green] {mtu_results['found_mtu']} байт")
    else:
        console.print(f"[yellow]⚠ {mtu_results['message']}[/yellow]")

async def perform_service_checks(report_data, cfg):
    """Performs connectivity checks for services defined in the config."""
    console.print("\n[bold cyan]Проверки Сервисов[/bold cyan]")
    services_to_check = cfg.get("services", [])
    inaccessible_domains_global = []

    # Get the current country from the network analysis report, if available
    current_country = report_data.get("network", {}).get("geo_ip", {}).get("country")
    if current_country:
        console.print(f"[bold blue]Обнаруженная страна агента: {current_country}[/bold blue]")
    else:
        console.print("[yellow]Не удалось определить страну агента для проверки гео-соответствия.[/yellow]")

    # Get IP reputation information
    reputation_info = report_data.get("network", {}).get("reputation", {})
    is_privacy_risk = reputation_info.get("is_privacy_risk", False)

    if is_privacy_risk:
        console.print("[bold red]❗ IP-адрес агента обнаружен как VPN/Прокси/Хостинг. Сервисы могут видеть ваше соединение как подозрительное.[/bold red]")


    for service in services_to_check:
        if not service.get("enabled", False):
            continue

        console.print(f"\n[bold magenta]Проверка сервиса {service['name']}[/bold magenta]")
        
        main_result = await check_service_connectivity(
            service["main_hostname"], service["name"], cfg["timeout"],
            service.get("expected_content_keywords"), service.get("blocked_content_keywords")
        )
        report_data.setdefault("services", {})[service["name"]] = {"main_host": main_result, "other_domains": {}}

        status_icon = "[green]✔[/green]" if main_result["status"] else "[red]✘[/red]"
        ping_info = f" ({main_result['ping_time']:.2f} мс)" if main_result["ping_time"] is not None else ""
        icon = service.get("icon", ":question:")
        
        console.print(f"{status_icon} {icon} {service['name']} (основной хост): {main_result['message']}{ping_info}")
        if main_result.get("advice"):
            for advice_item in main_result["advice"]:
                console.print(f"  [yellow]  Совет:[/yellow] {advice_item}")
        
        # Add advice if privacy risk detected
        if is_privacy_risk:
            main_result.setdefault("advice", []).append("Ваш IP-адрес обнаружен как VPN/Прокси/Хостинг. Сервис может видеть ваше соединение как подозрительное.")


        if main_result.get("inaccessible_domains"):
             for domain in main_result["inaccessible_domains"]:
                if (service['name'], domain) not in inaccessible_domains_global:
                    inaccessible_domains_global.append((service['name'], domain))
        
        for domain in service.get("domains", []):
             if domain != service["main_hostname"]:
                 domain_check_result = await check_domain_reachability(domain, resolver, cfg["timeout"])
                 report_data["services"][service["name"]]["other_domains"][domain] = domain_check_result
                 if not domain_check_result["status"]:
                     if (service['name'], domain) not in inaccessible_domains_global:
                         inaccessible_domains_global.append((service['name'], domain))



    if inaccessible_domains_global:
        unique_inaccessible_items = sorted(list(set([item[1] for item in inaccessible_domains_global])))
        report_data["inaccessible_domains"] = unique_inaccessible_items
        console.print("\n[bold red]Обнаружены недоступные домены:[/bold red]")
        for domain in unique_inaccessible_items:
            # Find the service name associated with the domain for context
            service_name = next((item[0] for item in inaccessible_domains_global if item[1] == domain), "N/A")
            console.print(f" • [red]{domain}[/red] (Сервис: {service_name})")
        
        console.print("\n[bold green]Рекомендуемый белый список для недоступных доменов:[/bold green]")
        for domain in unique_inaccessible_items:
            console.print(f" • {domain}")
        console.print("[yellow]Совет: Если вы столкнулись с блокировкой сервиса, попробуйте добавить эти домены в белый список вашего файервола/DNS-фильтра или используйте VPN/прокси.[/yellow]")

def save_report_if_enabled(report_data, cfg):
    """Saves the report if enabled in the configuration."""
    report_cfg = cfg.get("report", {})
    if not report_cfg.get("enabled", False):
        return

    filepath_template = report_cfg.get("filepath", "reports/netdiag_report_{timestamp}.txt")
    filepath = filepath_template.replace("{timestamp}", now().replace(" ", "_").replace(":", "-"))
    report_format = report_cfg.get("format", "json")
    
    if report_format == "json":
        content = json.dumps(report_data, indent=4, ensure_ascii=False)
    else:
        content = ""
        for section, data in report_data.items():
            content += f"--- {section.upper()} ---\n"
            if isinstance(data, dict):
                for key, value in data.items():
                    content += f"{key}: {json.dumps(value, indent=2, ensure_ascii=False)}\n"
            else:
                content += f"{json.dumps(data, indent=2, ensure_ascii=False)}\n"
            content += "\n"
    
    if save_report(filepath, content):
        console.print(f"\n[green]Отчет сохранен в {filepath}[/green]")
    else:
        console.print(f"\n[red]Не удалось сохранить отчет в {filepath}[/red]")

# A dictionary mapping check names to their functions and descriptions
AVAILABLE_CHECKS = {
    "network": {"func": perform_network_analysis, "desc": "Анализ сети и репутации IP"},
    "dns": {"func": perform_dns_lookup, "desc": "DNS Запрос (google.com)"},
    "dot_doh": {"func": perform_dot_doh_check, "desc": "Проверка DoT/DoH"},
    "icmp": {"func": perform_icmp_analysis, "desc": "Анализ ICMP (Ping, Traceroute)"},
    "tls": {"func": perform_tls_analysis, "desc": "Проверка SSL/TLS Сертификатов"},
    "mtu": {"func": perform_mtu_check, "desc": "Определение MTU"},
    "services": {"func": perform_service_checks, "desc": "Проверки Сервисов"},
    "dns_benchmark": {"func": run_dns_benchmark, "desc": "Бенчмарк DNS-резолверов"},
    "port_scan": {"func": run_port_scan, "desc": "Сканирование портов"},
}

async def run_specific_checks(checks_to_run: list, cfg, report_data):
    """Runs a specific list of diagnostic checks."""
    for check_name in checks_to_run:
        check_info = AVAILABLE_CHECKS.get(check_name)
        if check_info:
            check_func = check_info["func"]
            # DNS checks need different arguments than others
            if check_name == 'dns':
                 await check_func(report_data)
            else:
                 await check_func(report_data, cfg)
        else:
            console.print(f"[yellow]Предупреждение: Проверка '{check_name}' не найдена.[/yellow]")


async def run_all_checks(cfg, report_data):
    """Runs all available diagnostic checks."""
    await perform_network_analysis(report_data, cfg)
    await perform_dns_lookup(report_data)
    await perform_dot_doh_check(report_data, cfg)
    await perform_icmp_analysis(report_data, cfg)
    await perform_tls_analysis(report_data, cfg)
    await perform_mtu_check(report_data, cfg)
    await perform_service_checks(report_data, cfg)
    await run_dns_benchmark(report_data, cfg)
    await run_port_scan(report_data, cfg)


async def run(checks_to_run: list = None):
    """
    Main function to run the diagnostics.
    
    :param checks_to_run: A list of specific checks to run. If None, all checks are run.
    """
    cfg = load_config()
    
    console.print(
        Panel.fit(
            f"""[bold cyan]NetDiag[/bold cyan]
            Версия {get_version()}""",
            border_style="cyan"
        )
    )
    
    report_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": get_version(),
        "dns": {}, # Ensure 'dns' key exists
    }

    await initialize_resolver(cfg)

    if not await check_dependencies_and_report(report_data):
        return # Stop if dependencies are missing

    if checks_to_run:
        await run_specific_checks(checks_to_run, cfg, report_data)
    else:
        await run_all_checks(cfg, report_data)

    save_report_if_enabled(report_data, cfg)
