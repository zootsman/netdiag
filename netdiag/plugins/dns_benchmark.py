from ..plugin_manager import DiagnosticPlugin
from ..modules.dns_benchmark import run_dns_benchmark

class DNSBenchmarkPlugin(DiagnosticPlugin):
    """
    Plugin for running a DNS resolver benchmark.
    """
    name = "dns_benchmark"
    description = "Бенчмарк DNS-резолверов"

    async def run(self):
        """
        Pings all public DNS resolvers and recommends the fastest one.
        """
        await run_dns_benchmark(self.report_data, self.config)
