"""
dns_benchmark.py

Pings a list of public DNS resolvers to find the fastest one.
"""
import asyncio
from rich.console import Console
from rich.table import Table
from ..utils import ping_host

console = Console()

# List of public DNS resolvers
DNS_RESOLVERS = [
    {
        "name": "Google",
        "ips": ["8.8.8.8", "8.8.4.4"],
        "dot": "dns.google",
        "doh": "https://dns.google/dns-query"
    },
    {
        "name": "Cloudflare",
        "ips": ["1.1.1.1", "1.0.0.1"],
        "dot": "cloudflare-dns.com",
        "doh": "https://cloudflare-dns.com/dns-query"
    },
    {
        "name": "Quad9",
        "ips": ["9.9.9.9", "149.112.112.112"],
        "dot": "dns.quad9.net",
        "doh": "https://dns.quad9.net/dns-query"
    },
    {
        "name": "AdGuard",
        "ips": ["94.140.14.14", "94.140.15.15"],
        "dot": "dns.adguard.com",
        "doh": "https://dns.adguard.com/dns-query"
    },
    {
        "name": "OpenDNS",
        "ips": ["208.67.222.222", "208.67.220.220"],
        "dot": "N/A",
        "doh": "N/A"
    },
]

async def run_dns_benchmark(report_data: dict, cfg: dict):
    """
    Pings all public DNS resolvers and recommends the fastest one.
    """
    console.print("\n[bold cyan]Поиск оптимального DNS-резолвера[/bold cyan]")
    console.print("Пингуем общедоступные DNS-серверы, это может занять некоторое время...")

    results = []
    tasks = []

    # Create tasks for all IPs
    for resolver in DNS_RESOLVERS:
        for ip in resolver["ips"]:
            tasks.append(ping_host(ip))
    
    # Run pings in parallel
    ping_results = await asyncio.gather(*tasks)

    # Process results
    i = 0
    for resolver in DNS_RESOLVERS:
        latencies = []
        for ip in resolver["ips"]:
            latency = ping_results[i]
            if latency is not None:
                latencies.append(latency)
            i += 1
        
        avg_latency = sum(latencies) / len(latencies) if latencies else None
        results.append({
            "name": resolver["name"],
            "avg_latency": avg_latency,
            "ips": ", ".join(resolver["ips"]),
            "dot": resolver["dot"],
            "doh": resolver["doh"],
        })

    # Sort results by latency (handle None values)
    results.sort(key=lambda x: x["avg_latency"] if x["avg_latency"] is not None else float('inf'))

    # Display results in a table
    table = Table(title="Результаты DNS бенчмарка")
    table.add_column("Провайдер", justify="left", style="cyan")
    table.add_column("Средняя задержка (мс)", justify="center", style="magenta")
    table.add_column("IP-адреса", justify="left", style="green")

    for res in results:
        latency_str = f"{res['avg_latency']:.2f}" if res['avg_latency'] is not None else "N/A"
        table.add_row(res["name"], latency_str, res["ips"])
    
    console.print(table)

    # Make a recommendation
    best_resolver = results[0]
    if best_resolver and best_resolver["avg_latency"] is not None:
        console.print("\n[bold green]⭐ Рекомендация[/bold green]")
        console.print(f"Самая низкая задержка у [bold]{best_resolver['name']}[/bold].")
        console.print("Вы можете использовать следующие адреса:")
        table_rec = Table(show_header=False, box=None)
        table_rec.add_row("[bold]DNS:[/bold]", best_resolver['ips'])
        table_rec.add_row("[bold]DoT:[/bold]", best_resolver['dot'])
        table_rec.add_row("[bold]DoH:[/bold]", best_resolver['doh'])
        console.print(table_rec)
    else:
        console.print("\n[yellow]Не удалось определить лучший DNS-резолвер.[/yellow]")
        
    # Add to report data
    report_data["dns_benchmark"] = results

