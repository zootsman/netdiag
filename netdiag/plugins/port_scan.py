from ..plugin_manager import DiagnosticPlugin
from ..modules.port_scan import run_port_scan

class PortScanPlugin(DiagnosticPlugin):
    """
    Plugin for performing port scans on specified hosts.
    """
    name = "port_scan"
    description = "Сканирование портов"

    async def run(self):
        """
        Performs port scanning on hosts specified in the configuration.
        """
        await run_port_scan(self.report_data, self.config)
