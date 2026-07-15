from ..plugin_manager import DiagnosticPlugin
from ..modules.icmp import run_icmp_analysis

class ICMPPlugin(DiagnosticPlugin):
    """
    Plugin for ICMP analysis (Ping and Traceroute).
    """
    name = "icmp"
    description = "Анализ ICMP (Ping, Traceroute)"

    async def run(self):
        """
        Runs ICMP analysis and displays results.
        """
        self.console.print("\n[bold cyan]Анализ ICMP (Ping и Traceroute)[/bold cyan]")
        icmp_results = await run_icmp_analysis(self.config)
        self.report_data["icmp_analysis"] = icmp_results
        
        if not icmp_results.get("check_enabled"):
            self.console.print("[yellow]Проверка отключена в конфигурации.[/yellow]")
            return

        ping_failures = 0
        for host, result in icmp_results.get("ping_results", {}).items():
            if result["status"] == "ok":
                self.console.print(f"[green]✔ Ping {host}:[/green] {result['avg_latency_ms']:.2f} мс")
            else:
                self.console.print(f"[red]✘ Ping {host}:[/red] {result['error']}")
                ping_failures += 1
                
        if ping_failures > 0:
            self.console.print("\n[bold yellow]Обнаружены проблемы с ICMP (Ping).[/bold yellow]")
            self.console.print("  [bold]Объяснение:[/bold] Утилита ping отправляет ICMP-пакеты для проверки доступности хоста.")
            self.console.print("  Неудачные попытки могут означать, что хост выключен, недоступен из вашей сети, или что")
            self.console.print("  ICMP-трафик (используемый для ping) блокируется файерволом на пути к хосту или на самом хосте.")
            self.console.print("  [bold]Рекомендации:[/bold]")
            self.console.print("  • Убедитесь, что имя хоста написано правильно.")
            self.console.print("  • Попробуйте пинговать другие хосты, чтобы определить, является ли проблема специфичной для одного адреса.")
            self.console.print("  • Если все пинги не удаются, проверьте ваше интернет-соединение и настройки локального файервола.")

        traceroute_result = icmp_results.get("traceroute_result", {})
        if traceroute_result:
            self.console.print(f"\n[bold]Traceroute до {traceroute_result.get('host')}:[/bold]")
            if traceroute_result["status"] == "ok":
                self.console.print(f"[dim]{traceroute_result['output']}[/dim]")
            else:
                self.console.print(f"[red]Ошибка: {traceroute_result['output']}[/red]")
