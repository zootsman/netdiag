from ..plugin_manager import DiagnosticPlugin
from ..modules.tls import run_tls_analysis
from datetime import datetime

class TLSPlugin(DiagnosticPlugin):
    """
    Plugin for SSL/TLS certificate checks.
    """
    name = "tls"
    description = "Проверка SSL/TLS Сертификатов"

    async def run(self):
        """
        Runs TLS analysis and displays results.
        """
        self.console.print("\n[bold cyan]Проверка SSL/TLS Сертификатов[/bold cyan]")
        tls_results = await run_tls_analysis(self.config)
        self.report_data["tls_analysis"] = tls_results

        if not tls_results.get("check_enabled"):
            self.console.print("[yellow]Проверка отключена в конфигурации.[/yellow]")
            return

        warn_days = self.config.get("tls_check", {}).get("warn_days_before_expiry", 30)
        tls_errors = 0
        for host, result in tls_results.get("hosts", {}).items():
            self.console.print(f"\n[bold magenta]Сертификат для {host}[/bold magenta]")
            if result["status"] == "ok":
                self.console.print(f"  [green]Выдан:[/green] {result['issuer']}")
                self.console.print(f"  [green]Субъект:[/green] {result['subject']}")
                
                expiry_date = result['expires']
                if expiry_date:
                    self.console.print(f"  [green]Истекает:[/green] {expiry_date.strftime('%Y-%m-%d')}")
                    days_left = (expiry_date - datetime.now()).days
                    if days_left < 0:
                        self.console.print(f"  [bold red]❗ СЕРТИФИКАТ ИСТЕК {abs(days_left)} дней назад[/bold red]")
                        tls_errors += 1
                    elif days_left < warn_days:
                        self.console.print(f"  [bold yellow]⚠ Истекает через {days_left} дней[/bold yellow]")
                else:
                    self.console.print("  [yellow]Не удалось определить дату истечения.[/yellow]")
            else:
                self.console.print(f"  [red]Ошибка: {result['error']}[/red]")
                tls_errors += 1
                
        if tls_errors > 0:
            self.console.print("\n[bold red]Обнаружены серьезные проблемы с SSL/TLS сертификатами![/bold red]")
            self.console.print("  [bold]Объяснение:[/bold] SSL/TLS сертификаты используются для шифрования трафика и подтверждения подлинности сайтов.")
            self.console.print("  Ошибки (истекший срок действия, неверное имя хоста, недоверенный издатель) могут указывать на попытку")
            self.console.print("  перехвата вашего трафика (атака 'человек-по-середине', Man-in-the-Middle).")
            self.console.print("  [bold]Рекомендации:[/bold]")
            self.console.print("  • [bold red]КРАЙНЕ НЕ РЕКОМЕНДУЕТСЯ[/bold red] передавать чувствительные данные (пароли, номера карт) сайтам с ошибками сертификатов.")
            self.console.print("  • Проблема может быть на стороне сервера. Если вы не доверяете сети, воздержитесь от использования ресурса.")
            self.console.print("  • Убедитесь, что системное время на вашем устройстве настроено правильно, так как это влияет на проверку сертификатов.")
