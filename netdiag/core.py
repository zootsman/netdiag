from rich.console import Console
from rich.panel import Panel
from datetime import datetime
import json

from .version import get_version
from .dependency import check_dependencies
from .config import load_config
from .plugin_manager import PluginManager # Import PluginManager

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

# AVAILABLE_CHECKS is now part of PluginManager after discovery
# This dictionary will be dynamically populated in PluginManager

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
    plugin_manager.discover_plugins() # Discover plugins dynamically
    
    # After discovery, we can get the available checks from the plugin manager
    # This is a temporary placeholder; ideally, netdiag.py would get this directly
    # from PluginManager or a centralized source.
    # For now, we still need AVAILABLE_CHECKS in netdiag.py, so it will be
    # generated from plugin_manager.plugins.
    # This will be addressed in a later step (suggestion #5)
    
    if checks_to_run:
        await plugin_manager.run_specific(checks_to_run)
    else:
        await plugin_manager.run_all()

    save_report_if_enabled(report_data, cfg)

