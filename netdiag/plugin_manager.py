"""
plugin_manager.py

A simple plugin manager for the diagnostic checks.
"""

class DiagnosticPlugin:
    """
    Base class for all diagnostic plugins.
    """
    def __init__(self, console, config, report_data):
        self.console = console
        self.config = config
        self.report_data = report_data

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
    def __init__(self, console, config, report_data):
        self.console = console
        self.config = config
        self.report_data = report_data
        self.plugins = []

    def register(self, plugin_class):
        """
        Registers a plugin class.
        """
        self.plugins.append(plugin_class)

    async def run_all(self):
        """
        Runs all registered plugins.
        """
        for plugin_class in self.plugins:
            plugin_instance = plugin_class(self.console, self.config, self.report_data)
            await plugin_instance.run()

    async def run_specific(self, check_names: list):
        """
        Runs only the specified plugins.
        """
        for plugin_class in self.plugins:
            if getattr(plugin_class, 'name', None) in check_names:
                plugin_instance = plugin_class(self.console, self.config, self.report_data)
                await plugin_instance.run()
