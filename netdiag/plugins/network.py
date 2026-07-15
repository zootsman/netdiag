from ..plugin_manager import DiagnosticPlugin
from ..modules.network import get_public_ip
from ..modules.reputation import check_ip_reputation
from ..modules.cdn import check_cdn_info
from ..utils import get_geo_ip_info

class NetworkPlugin(DiagnosticPlugin):
    """
    Plugin for network analysis, including public IP, GeoIP, and IP reputation.
    """
    name = "network"
    description = "Анализ сети и репутации IP"

    async def run(self):
        """
        Gets public IP, GeoIP info, and IP reputation.
        """
        self.console.print("\n[bold cyan]Анализ сети и репутации IP[/bold cyan]")
        self.report_data["network"] = {}
        ip = await get_public_ip(self.config["timeout"])
        self.report_data["network"]["public_ip"] = ip if ip else "N/A"

        if not ip:
            self.console.print("[red]Не удалось определить публичный IP[/red]")
            return

        self.console.print(f"[green]Публичный IPv4:[/green] {ip}")
        
        # Geo-IP Info
        geo_info = await get_geo_ip_info(ip)
        self.report_data["network"]["geo_ip"] = geo_info
        if geo_info.get("status") == "success":
            country = geo_info.get("country", "N/A")
            city = geo_info.get("city", "N/A")
            isp = geo_info.get("isp", "N/A")
            self.console.print(f"[green]Местоположение:[/green] {city}, {country}")
            self.console.print(f"[green]Провайдер:[/green] {isp}")
        else:
            self.console.print("[yellow]Не удалось определить Geo-IP информацию.[/yellow]")

        # IP Reputation Check
        reputation_info = await check_ip_reputation(ip, self.config)
        self.report_data["network"]["reputation"] = reputation_info
        
        if not reputation_info["check_enabled"]:
            self.console.print(f"[yellow]{reputation_info['message']}[/yellow]")
            return

        self.console.print("\n[bold]Проверка репутации IP:[/bold]")
        has_errors = False
        for provider_data in reputation_info["providers_data"]:
            if provider_data.get("has_error"):
                self.console.print(f"  [yellow]• {provider_data['provider']}: {provider_data['message']}[/yellow]")
                has_errors = True
            elif provider_data.get("vpn") or provider_data.get("proxy") or provider_data.get("tor") or provider_data.get("hosting"):
                issues = []
                if provider_data.get("vpn"): issues.append("VPN")
                if provider_data.get("proxy"): issues.append("Прокси")
                if provider_data.get("tor"): issues.append("Tor")
                if provider_data.get("hosting"): issues.append("Хостинг")
                self.console.print(f"  [red]• {provider_data['provider']}: Обнаружено: {', '.join(issues)}[/red]")
            else:
                self.console.print(f"  [green]• {provider_data['provider']}: Риски не обнаружены[/green]")

        if reputation_info["is_privacy_risk"]:
            self.console.print(f"\n[red]❗ Общий результат: {reputation_info['message']}[/red]")
            self.console.print("  [bold]Объяснение:[/bold] Ваш IP-адрес определяется некоторыми сервисами как VPN, прокси, Tor или хостинг.")
            self.console.print("  Это может влиять на доступ к некоторым сайтам, которые блокируют такой трафик для защиты от спама и мошенничества.")
        elif not has_errors:
            self.console.print(f"\n[green]✔ Общий результат: {reputation_info['message']}[/green]")
        
        if has_errors:
            self.console.print("\n[bold yellow]Примечание по ошибкам API:[/bold yellow]")
            self.console.print("  Некоторые API для проверки репутации могут иметь ограничения на количество бесплатных запросов.")
            self.console.print("  Ошибки, связанные с лимитом, обычно решаются сами собой через некоторое время.")

        # CDN Check
        cdn_info = await check_cdn_info(ip, self.config["timeout"])
        self.report_data["network"]["cdn"] = cdn_info
        if cdn_info["cdn_detected"]:
            self.console.print(f"[green]✔ CDN Обнаружен:[/green] {cdn_info['provider']}")
            if cdn_info["edge_location"]:
                self.console.print(f"[green]  Edge Location:[/green] {cdn_info['edge_location']}")
            if cdn_info["country"]:
                self.console.print(f"[green]  Страна CDN:[/green] {cdn_info['country']}")
        else:
            self.console.print(f"[yellow]{cdn_info['message']}[/yellow]")
