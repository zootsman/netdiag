from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json

from .version import get_version
from .dependency import check_dependencies
from .config import load_config
from .plugin_manager import PluginManager

# Import all plugins
from .plugins.network import NetworkPlugin
from .plugins.dns import DNSPlugin
from .plugins.dot_doh import DotDohPlugin
from .plugins.icmp import ICMPPlugin
from .plugins.tls import TLSPlugin
from .plugins.mtu import MTUPlugin
from .plugins.services import ServicesPlugin
from .plugins.dns_benchmark import DNSBenchmarkPlugin
from .plugins.port_scan import PortScanPlugin

from .modules.dns import initialize_resolver
from .utils import save_report, now

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
    "network": {"func": NetworkPlugin, "desc": "Анализ сети и репутации IP"},
    "dns": {"func": DNSPlugin, "desc": "DNS Запрос (google.com)"},
    "dot_doh": {"func": DotDohPlugin, "desc": "Проверка DoT/DoH"},
    "icmp": {"func": ICMPPlugin, "desc": "Анализ ICMP (Ping, Traceroute)"},
    "tls": {"func": TLSPlugin, "desc": "Проверка SSL/TLS Сертификатов"},
    "mtu": {"func": MTUPlugin, "desc": "Определение MTU"},
    "services": {"func": ServicesPlugin, "desc": "Проверки Сервисов"},
    "dns_benchmark": {"func": DNSBenchmarkPlugin, "desc": "Бенчмарк DNS-резолверов"},
    "port_scan": {"func": PortScanPlugin, "desc": "Сканирование портов"},
}

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
    
    plugin_manager = PluginManager(console, cfg, report_data)
    
    # Register all plugins
    for check in AVAILABLE_CHECKS.values():
        plugin_manager.register(check['func'])

    if checks_to_run:
        await plugin_manager.run_specific(checks_to_run)
    else:
        await plugin_manager.run_all()

    save_report_if_enabled(report_data, cfg)

