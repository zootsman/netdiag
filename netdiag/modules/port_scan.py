"""
port_scan.py

Performs port scanning on specified hosts.
"""

import asyncio
from rich.console import Console
from rich.table import Table

console = Console()

async def scan_port(host: str, port: int, timeout: float) -> bool:
    """
    Attempts to connect to a given port on a host. Returns True if successful, False otherwise.
    """
    try:
        # asyncio.open_connection attempts to establish a TCP connection
        # If successful, it means the port is open
        # We don't need reader/writer, just the connection attempt
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return False
    except Exception:
        return False

async def run_port_scan(report_data: dict, cfg: dict):
    """
    Performs port scanning on hosts specified in the configuration.
    """
    port_scan_cfg = cfg.get("port_scan", {})
    
    results = {
        "check_enabled": port_scan_cfg.get("enabled", False),
        "hosts": {}
    }

    if not results["check_enabled"]:
        console.print("[yellow]Сканирование портов отключено в конфигурации.[/yellow]")
        return results

    target_hosts = port_scan_cfg.get("hosts", [])
    default_ports = port_scan_cfg.get("default_ports", [80, 443, 21, 22, 23, 25, 110, 143, 3389])
    timeout_per_port = port_scan_cfg.get("timeout_per_port", 0.5)

    if not target_hosts:
        console.print("[yellow]Хосты для сканирования портов не указаны в конфигурации.[/yellow]")
        return results

    console.print("\n[bold cyan]Сканирование портов[/bold cyan]")
    
    overall_table = Table(title="Результаты сканирования портов", show_lines=True)
    overall_table.add_column("Хост", style="cyan", justify="left")
    overall_table.add_column("Открытые порты", style="green", justify="left")
    overall_table.add_column("Закрытые/фильтруемые порты", style="red", justify="left")

    for host in target_hosts:
        open_ports_set = set()
        closed_ports_set = set()
        
        tasks = []
        for port in default_ports:
            tasks.append(scan_port(host, port, timeout_per_port))
        
        scan_results = await asyncio.gather(*tasks)

        for port, is_open in zip(default_ports, scan_results):
            if is_open:
                open_ports_set.add(str(port))
            else:
                closed_ports_set.add(str(port))

        host_results = {
            "open_ports": sorted(list(open_ports_set), key=int),
            "closed_ports": sorted(list(closed_ports_set), key=int),
            "errored_ports": [] # Not directly handled by sets, keep as is for now
        }
        results["hosts"][host] = host_results

        overall_table.add_row(
            host,
            ", ".join(host_results["open_ports"]) if host_results["open_ports"] else "[yellow]Нет[/yellow]",
            ", ".join(host_results["closed_ports"]) if host_results["closed_ports"] else "[green]Нет[/green]"
        )
            
    console.print(overall_table)

    # Add to report data
    report_data["port_scan"] = results
    
    return results
