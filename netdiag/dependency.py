import importlib
from .utils import command_exists

REQUIRED_MODULES = {
    "requests": "requests",
    "rich": "rich",
    "httpx": "httpx",
    "dns": "dnspython"
}

REQUIRED_COMMANDS = {
    "ping": "ping",
    "traceroute": "traceroute"
}


def check_dependencies(console):
    console.print("\n[bold cyan]Проверка зависимостей[/bold cyan]")

    missing = []

    # Check for Python modules
    for module, package in REQUIRED_MODULES.items():
        try:
            importlib.import_module(module)
            console.print(f"[green]✔[/green] {package} (Python модуль)")
        except ImportError:
            console.print(f"[red]✘[/red] {package} (Python модуль)")
            missing.append(package)

    # Check for command-line tools
    for command, name in REQUIRED_COMMANDS.items():
        if command_exists(command):
            console.print(f"[green]✔[/green] {name} (Команда)")
        else:
            console.print(f"[red]✘[/red] {name} (Команда)")
            missing.append(name)

    return missing