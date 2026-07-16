"""
plugin_manager.py

A simple plugin manager for the diagnostic checks.
"""

"""
plugin_manager.py

A simple plugin manager for the diagnostic checks.
"""

import os
import importlib.util
from inspect import isclass
from pathlib import Path
from abc import ABC, abstractmethod # Import ABC and abstractmethod

class DiagnosticPlugin(ABC): # Inherit from ABC
    """
    Base class for all diagnostic plugins.
    """
    def __init__(self, console, config, report_data):
        self.console = console
        self.config = config
        self.report_data = report_data
        # Ensure plugin_name is always set from the abstract 'name' property.
        self.plugin_name = self.name # Use the abstract property 'name'

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The unique name of the plugin, used for CLI arguments and report keys.
        Must be implemented by subclasses.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        A short description of the plugin, used for CLI help messages.
        Must be implemented by subclasses.
        """
        pass

    async def run(self):
        """
        Run the diagnostic check.
        This method must be overridden by subclasses.
        """
        raise NotImplementedError

class PluginManager:
    """
    A simple plugin manager that registers and runs diagnostic plugins.
    """
    PLUGIN_DIR = Path(__file__).parent / "plugins"

    def __init__(self, console, config, report_data):
        self.console = console
        self.config = config
        self.report_data = report_data
        self.plugins = []
        self._available_checks = {} # Stores {check_name: {'func': plugin_class, 'desc': 'description'}}

    def register(self, plugin_class):
        """
        Registers a plugin class and stores its info.
        Assumes plugin_class has 'name' and 'description' abstract properties.
        """
        self.plugins.append(plugin_class)
        check_name = plugin_class.name
        check_desc = plugin_class.description
        self._available_checks[check_name] = {'func': plugin_class, 'desc': check_desc}


    def discover_plugins(self):
        """
        Discovers and registers all plugins in the PLUGIN_DIR.
        """
        if not self.PLUGIN_DIR.is_dir():
            self.console.print(f"[red]Ошибка: Директория плагинов не найдена: {self.PLUGIN_DIR}[/red]")
            return

        for plugin_file in self.PLUGIN_DIR.glob("*.py"):
            if plugin_file.name == "__init__.py":
                continue

            module_name = f"netdiag.plugins.{plugin_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec is None:
                self.console.print(f"[red]Ошибка: Не удалось создать спецификацию для {plugin_file}[/red]")
                continue

            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in module.__dict__.items():
                    # Check if it's a class, a subclass of DiagnosticPlugin, and not DiagnosticPlugin itself
                    # Also ensure it's not an abstract class (has 'name' and 'description' implemented)
                    if (isclass(obj) and issubclass(obj, DiagnosticPlugin) and obj is not DiagnosticPlugin
                            and not getattr(obj, '__abstractmethods__', False)):
                        self.register(obj)
                        break # Assume one concrete plugin class per file
            except Exception as e:
                self.console.print(f"[red]Ошибка при загрузке плагина {plugin_file.name}: {e}[/red]")
                
    def get_available_checks_info(self):
        """
        Returns a dictionary of available checks and their descriptions.
        """
        return self._available_checks

    async def run_all(self):
        """
        Runs all registered plugins.
        """
        for check_name, info in self._available_checks.items():
            plugin_class = info['func']
            plugin_instance = plugin_class(self.console, self.config, self.report_data)
            await plugin_instance.run()

    async def run_specific(self, check_names: list):
        """
        Runs only the specified plugins.
        """
        for check_name in check_names:
            info = self._available_checks.get(check_name)
            if info:
                plugin_class = info['func']
                plugin_instance = plugin_class(self.console, self.config, self.report_data)
                await plugin_instance.run()
            else:
                self.console.print(f"[yellow]Предупреждение: Плагин '{check_name}' не найден и будет пропущен.[/yellow]")

