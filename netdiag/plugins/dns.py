from ..plugin_manager import DiagnosticPlugin
from ..modules.dns import lookup_dns

class DNSPlugin(DiagnosticPlugin):
    """
    Plugin for basic DNS lookups.
    """
    name = "dns"
    description = "DNS Запрос (google.com)"

    async def run(self):
        """
        Performs a DNS lookup for google.com.
        """
        self.console.print("\n[bold cyan]DNS Запрос (google.com)[/bold cyan]")
        dns_results = await lookup_dns("google.com")
        self.report_data["dns"]["google_com_lookup"] = dns_results

        for record_type, records in dns_results.items():
            if records:
                self.console.print(f"[green]{record_type} записи:[/green]")
                for record in records:
                    self.console.print(f" • {record}")
            else:
                self.console.print(f"[yellow]Нет {record_type} записей или ошибка.[/yellow]")
