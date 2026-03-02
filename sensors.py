import psutil
import time
from collections import deque


class SystemSensor:
    def __init__(self, history_size=10):
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.ram_history = deque(maxlen=history_size)
        self.net_history = deque(maxlen=history_size)
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()

    def update(self):
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None) / 100.0
        self.cpu_history.append(cpu_percent)

        # RAM
        ram = psutil.virtual_memory()
        ram_percent = ram.percent / 100.0
        self.ram_history.append(ram_percent)

        # Net
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        elapsed = current_time - self.last_time

        if elapsed > 0:
            bytes_sent = current_net_io.bytes_sent - self.last_net_io.bytes_sent
            bytes_recv = current_net_io.bytes_recv - self.last_net_io.bytes_recv
            # Normalize net usage (assuming 10MB/s is "high" for ambient context)
            total_speed = (bytes_sent + bytes_recv) / elapsed
            net_normalized = min(total_speed / 10_000_000.0, 1.0)
            self.net_history.append(net_normalized)

        self.last_net_io = current_net_io
        self.last_time = current_time

    def get_smoothed_metrics(self):
        """Returns smoothed (0.0 - 1.0) metrics for audio mapping."""
        if not self.cpu_history:
            return 0.0, 0.0, 0.0

        avg_cpu = sum(self.cpu_history) / len(self.cpu_history)
        avg_ram = sum(self.ram_history) / len(self.ram_history)
        avg_net = (
            sum(self.net_history) / len(self.net_history) if self.net_history else 0.0
        )

        return avg_cpu, avg_ram, avg_net
