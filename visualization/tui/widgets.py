from textual.widgets import Static, RichLog
from textual.containers import Container, Vertical
from rich.text import Text


class HeaderWidget(Static):
    """Top header bar with connection status"""

    DEFAULT_CSS = """
    HeaderWidget {
        width: 100%;
        height: 3;
        background: #1e3a5f;
        color: white;
        text-align: center;
        padding: 1;
    }
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 54321):
        super().__init__()
        self.host = host
        self.port = port
        self.mode = "DEMO"
        self.connected = False

    def compose_header(self) -> Text:
        status = "CONNECTED" if self.connected else "DISCONNECTED"
        status_color = "green" if self.connected else "red"
        
        text = Text()
        text.append("⚡ LOBSTER HFT ENGINE v1.0", style="bold white")
        text.append(" │ ", style="dim white")
        text.append(f"{status}: ", style=f"bold {status_color}")
        text.append(f"{self.host}:{self.port}", style="white")
        text.append(" │ ", style="dim white")
        text.append(f"MODE: {self.mode}", style="bold cyan")
        return text

    def on_mount(self):
        self.update(self.compose_header())

    def set_connected(self, connected: bool):
        self.connected = connected
        self.update(self.compose_header())


class AlgoPanel(Vertical):
    """Left panel showing generated orders"""

    DEFAULT_CSS = """
    AlgoPanel {
        width: 30;
        min-width: 30;
        height: 100%;
        border: solid #3a7bd5;
        background: #0a0a0f;
    }
    
    AlgoPanel > Static {
        height: 3;
        padding: 1;
        background: #1a1a2e;
        color: #3a7bd5;
        text-align: center;
        text-style: bold;
    }
    
    AlgoPanel > RichLog {
        height: 1fr;
        padding: 0 1;
    }
    """

    def compose(self):
        yield Static("ORDERS")
        yield RichLog(id="algo-log", highlight=True, markup=True)

    def log_order(self, side: str, quantity: int, price: int):
        log = self.query_one("#algo-log", RichLog)
        if side == "BUY":
            log.write(Text(f">> SENT: BUY {quantity} @ {price}", style="bold green"))
        else:
            log.write(Text(f">> SENT: SELL {quantity} @ {price}", style="bold red"))


class TapePanel(Vertical):
    """Center panel showing exchange responses"""

    DEFAULT_CSS = """
    TapePanel {
        width: 2fr;
        height: 100%;
        border: solid #00d9ff;
        background: #0a0a0f;
    }
    
    TapePanel > Static {
        height: 3;
        padding: 1;
        background: #1a1a2e;
        color: #00d9ff;
        text-align: center;
        text-style: bold;
    }
    
    TapePanel > RichLog {
        height: 1fr;
        padding: 0 1;
    }
    """

    def compose(self):
        yield Static("EXCHANGE TAPE")
        yield RichLog(id="tape-log", highlight=True, markup=True)

    def log_message(self, message: str):
        log = self.query_one("#tape-log", RichLog)
        
        if "Trade" in message or "MATCH" in message or "Executed" in message:
            text = Text()
            # text.append("", style="") 
            text.append("[EXEC] ", style="bold bright_yellow")
            text.append(message, style="bold bright_green on #1a3d1a")
            log.write(text)
        elif "placed" in message or "Accepted" in message:
            log.write(Text(f"    [ACK] {message}", style="dim"))
        elif "canceled" in message:
            log.write(Text(f"    [CXL] {message}", style="yellow"))
        else:
            log.write(Text(f"    [MSG] {message}", style="white"))


class TelemetryPanel(Vertical):
    """Right panel with live stats and engine specs"""

    DEFAULT_CSS = """
    TelemetryPanel {
        width: 35;
        min-width: 35;
        height: 100%;
        border: solid #ff6b6b;
        background: #0a0a0f;
    }
    
    TelemetryPanel > Static {
        height: 3;
        padding: 1;
        background: #1a1a2e;
        color: #ff6b6b;
        text-align: center;
        text-style: bold;
    }
    
    #live-stats {
        height: auto;
        min-height: 10;
        padding: 1;
        background: #0f0f1a;
        border: solid #333;
        margin: 1;
    }
    
    #engine-specs {
        height: auto;
        min-height: 10;
        padding: 1;
        background: #0f0f1a;
        border: solid #333;
        margin: 1;
    }
    """

    def compose(self):
        yield Static("TELEMETRY & SPECS")
        yield Static(id="live-stats")
        yield Static(id="engine-specs")

    def on_mount(self):
        self._update_specs()
        self._update_stats(0, 0, 0.0, "MARKET_MAKING")

    def _update_specs(self):
        specs_widget = self.query_one("#engine-specs", Static)
        
        text = Text()
        text.append("ENGINE BENCHMARKS\n", style="bold yellow")
        text.append("─" * 25 + "\n", style="dim")
        text.append("Core Latency:  ", style="cyan")
        text.append("440 ns\n", style="bold green")
        text.append("Wire Latency:  ", style="cyan")
        text.append("33 μs\n", style="bold green")
        text.append("Throughput:    ", style="cyan")
        text.append("2.2M/s\n", style="bold green")
        text.append("Concurrency:   ", style="cyan")
        text.append("Multi-Threaded\n", style="bold green")
        text.append("Sync:          ", style="cyan")
        text.append("Mutex-Guarded", style="bold green")
        
        specs_widget.update(text)

    def _update_stats(self, orders: int, volume: int, rate: float, strategy: str):
        stats_widget = self.query_one("#live-stats", Static)
        
        text = Text()
        text.append("🔴 LIVE SESSION\n", style="bold red")
        text.append("─" * 25 + "\n", style="dim")
        text.append("Orders Sent:   ", style="white")
        text.append(f"{orders:,}\n", style="bold bright_green")
        text.append("Total Volume:  ", style="white")
        text.append(f"{volume:,}\n", style="bold bright_green")
        text.append("Rate:          ", style="white")
        text.append(f"{rate:.1f}/s\n", style="bold bright_cyan")
        text.append("Strategy:      ", style="white")
        text.append(strategy, style="bold yellow")
        
        stats_widget.update(text)

    def update_live_stats(self, orders: int, volume: int, rate: float, strategy: str):
        self._update_stats(orders, volume, rate, strategy)


class FooterWidget(Static):
    """Bottom footer with controls info"""

    DEFAULT_CSS = """
    FooterWidget {
        width: 100%;
        height: 3;
        background: #1a1a2e;
        color: #888;
        text-align: center;
        padding: 1;
    }
    """

    def on_mount(self):
        text = Text()
        text.append("[Q]", style="bold cyan")
        text.append(" Quit  ", style="dim")
        text.append("[1-3]", style="bold cyan")
        text.append(" Strategy  ", style="dim")
        text.append("[+/-]", style="bold cyan")
        text.append(" Speed  ", style="dim")
        text.append("[SPACE]", style="bold cyan")
        text.append(" Pause/Resume  ", style="dim")
        text.append("[R]", style="bold cyan")
        text.append(" Reset Stats", style="dim")
        self.update(text)
