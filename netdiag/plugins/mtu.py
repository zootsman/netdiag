from ..plugin_manager import DiagnosticPlugin
from ..modules.mtu import run_mtu_check

class MTUPlugin(DiagnosticPlugin):
    """
    Plugin for MTU discovery.
    """
    name = "mtu"
    description = "Определение MTU"

    async def run(self):
        """
        Runs MTU check and displays results.
        """
        self.console.print("\n[bold cyan]Определение MTU[/bold cyan]")
        mtu_results = await run_mtu_check(self.config)
        self.report_data["mtu_discovery"] = mtu_results

        if not mtu_results.get("check_enabled"):
            self.console.print("[yellow]Проверка отключена в конфигурации.[/yellow]")
            return
            
        if mtu_results.get("found_mtu"):
            self.console.print(f"[green]✔ Оптимальный MTU:[/green] {mtu_results['found_mtu']} байт")
        else:
            self.console.print(f"[yellow]⚠ {mtu_results['message']}[/yellow]")
