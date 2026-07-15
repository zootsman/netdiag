from ..plugin_manager import DiagnosticPlugin
from ..utils import check_service_connectivity, check_domain_reachability
from ..modules.dns import resolver

class ServicesPlugin(DiagnosticPlugin):
    """
    Plugin for checking connectivity to various services.
    """
    name = "services"
    description = "Проверки Сервисов"

    async def run(self):
        """
        Performs connectivity checks for services defined in the config.
        """
        self.console.print("\n[bold cyan]Проверки Сервисов[/bold cyan]")
        services_to_check = self.config.get("services", [])
        inaccessible_domains_global = []

        # Get the current country from the network analysis report, if available
        current_country = self.report_data.get("network", {}).get("geo_ip", {}).get("country")
        if current_country:
            self.console.print(f"[bold blue]Обнаруженная страна агента: {current_country}[/bold blue]")
        else:
            self.console.print("[yellow]Не удалось определить страну агента для проверки гео-соответствия.[/yellow]")

        # Get IP reputation information
        reputation_info = self.report_data.get("network", {}).get("reputation", {})
        is_privacy_risk = reputation_info.get("is_privacy_risk", False)

        if is_privacy_risk:
            self.console.print("[bold red]❗ IP-адрес агента обнаружен как VPN/Прокси/Хостинг. Сервисы могут видеть ваше соединение как подозрительное.[/bold red]")


        for service in services_to_check:
            if not service.get("enabled", False):
                continue

            self.console.print(f"\n[bold magenta]Проверка сервиса {service['name']}[/bold magenta]")
            
            main_result = await check_service_connectivity(
                service["main_hostname"], service["name"], self.config["timeout"],
                service.get("expected_content_keywords"), service.get("blocked_content_keywords")
            )
            self.report_data.setdefault("services", {})[service["name"]] = {"main_host": main_result, "other_domains": {}}

            status_icon = "[green]✔[/green]" if main_result["status"] else "[red]✘[/red]"
            ping_info = f" ({main_result['ping_time']:.2f} мс)" if main_result["ping_time"] is not None else ""
            icon = service.get("icon", ":question:")
            
            self.console.print(f"{status_icon} {icon} {service['name']} (основной хост): {main_result['message']}{ping_info}")
            if main_result.get("advice"):
                for advice_item in main_result["advice"]:
                    self.console.print(f"  [yellow]  Совет:[/yellow] {advice_item}")
            
            # Add advice if privacy risk detected
            if is_privacy_risk:
                main_result.setdefault("advice", []).append("Ваш IP-адрес обнаружен как VPN/Прокси/Хостинг. Сервис может видеть ваше соединение как подозрительное.")


            if main_result.get("inaccessible_domains"):
                 for domain in main_result["inaccessible_domains"]:
                    if (service['name'], domain) not in inaccessible_domains_global:
                        inaccessible_domains_global.append((service['name'], domain))
            
            for domain in service.get("domains", []):
                 if domain != service["main_hostname"]:
                     domain_check_result = await check_domain_reachability(domain, resolver, self.config["timeout"])
                     self.report_data["services"][service["name"]]["other_domains"][domain] = domain_check_result
                     if not domain_check_result["status"]:
                         if (service['name'], domain) not in inaccessible_domains_global:
                             inaccessible_domains_global.append((service['name'], domain))



        if inaccessible_domains_global:
            unique_inaccessible_items = sorted(list(set([item[1] for item in inaccessible_domains_global])))
            self.report_data["inaccessible_domains"] = unique_inaccessible_items
            self.console.print("\n[bold red]Обнаружены недоступные домены:[/bold red]")
            for domain in unique_inaccessible_items:
                # Find the service name associated with the domain for context
                service_name = next((item[0] for item in inaccessible_domains_global if item[1] == domain), "N/A")
                self.console.print(f" • [red]{domain}[/red] (Сервис: {service_name})")
            
            self.console.print("\n[bold green]Рекомендуемый белый список для недоступных доменов:[/bold green]")
            for domain in unique_inaccessible_items:
                self.console.print(f" • {domain}")
            self.console.print("[yellow]Совет: Если вы столкнулись с блокировкой сервиса, попробуйте добавить эти домены в белый список вашего файервола/DNS-фильтра или используйте VPN/прокси.[/yellow]")
