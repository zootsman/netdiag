from ..plugin_manager import DiagnosticPlugin
from ..modules.dns import check_dot, check_doh

class DotDohPlugin(DiagnosticPlugin):
    """
    Plugin for checking DoT/DoH server availability.
    """
    name = "dot_doh"
    description = "Проверка DoT/DoH"

    async def run(self):
        """
        Проверяет поддержку DoT/DoH на предварительно настроенных публичных DNS-серверах.
        """
        self.console.print("\n[bold cyan]Проверка доступности публичных DoT/DoH серверов[/bold cyan]")
        
        check_cfg = self.config.get("dot_doh_check", {})
        if not check_cfg.get("enabled"):
            self.console.print("[yellow]Проверка DoT/DoH отключена в конфигурации.[/yellow]")
            self.report_data["dns"]["dot_doh_checks"] = {"status": "disabled"}
            return

        servers_to_check = check_cfg.get("servers", [])
        if not servers_to_check:
            self.console.print("[yellow]Нет серверов для проверки DoT/DoH в конфигурации.[/yellow]")
            self.report_data["dns"]["dot_doh_checks"] = {"status": "no_servers_configured"}
            return

        self.report_data["dns"]["dot_doh_checks"] = {}
        timeout = self.config.get("timeout", 5)
        overall_failure = False

        for server in servers_to_check:
            server_name = server.get("name", "N/A")
            self.console.print(f"\n[bold magenta]Проверка сервера: {server_name}[/bold magenta]")
            self.report_data["dns"]["dot_doh_checks"][server_name] = {}

            # Проверка DoT
            dot_host = server.get("dot_host")
            dot_ip = server.get("ip")
            if dot_host and dot_ip:
                dot_supported = await check_dot(dot_host, dot_ip, timeout)
                self.report_data["dns"]["dot_doh_checks"][server_name]["dot"] = dot_supported
                if dot_supported:
                    self.console.print(f"[green]✔ DoT ({dot_host}) поддерживается[/green]")
                else:
                    self.console.print(f"[red]✘ DoT ({dot_host}) не поддерживается или заблокирован[/red]")
                    overall_failure = True
            else:
                self.report_data["dns"]["dot_doh_checks"][server_name]["dot"] = "not_configured"

            # Проверка DoH
            doh_url = server.get("doh_url")
            if doh_url:
                doh_supported = await check_doh(doh_url, timeout)
                self.report_data["dns"]["dot_doh_checks"][server_name]["doh"] = doh_supported
                if doh_supported:
                    self.console.print(f"[green]✔ DoH ({doh_url}) поддерживается[/green]")
                else:
                    self.console.print(f"[red]✘ DoH ({doh_url}) не поддерживается или заблокирован[/red]")
                    overall_failure = True
            else:
                self.report_data["dns"]["dot_doh_checks"][server_name]["doh"] = "not_configured"

        if overall_failure:
            self.console.print("\n[bold yellow]Обнаружены проблемы с доступностью защищенных DNS-серверов.[/bold yellow]")
            self.console.print("  [bold]Объяснение:[/bold] Протоколы DNS-over-TLS (DoT) и DNS-over-HTTPS (DoH) шифруют ваши DNS-запросы,")
            self.console.print("  повышая приватность и безопасность. Если эти серверы недоступны, это может быть признаком")
            self.console.print("  блокировки со стороны вашего интернет-провайдера (ISP) или сетевого экрана.")
            self.console.print("  [bold]Рекомендации:[/bold]")
            self.console.print("  • Попробуйте использовать VPN для обхода возможных блокировок.")
            self.console.print("  • Проверьте настройки вашего роутера или файервола на предмет блокировки портов 853 (DoT) или 443 (DoH).")
            self.console.print("  • Вы можете настроить системный DNS на один из работающих серверов, если таковые имеются.")
