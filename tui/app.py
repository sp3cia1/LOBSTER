import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.binding import Binding

from .connection import AsyncTCPConnection, ServerConfig, ConnectionState
from .generator import OrderGenerator
from .widgets import HeaderWidget, AlgoPanel, TapePanel, TelemetryPanel, FooterWidget


class LobsterApp(App):
    """LOBSTER HFT Engine TUI Application"""

    CSS = """
    Screen {
        background: #0a0a0f;
    }
    
    #main-container {
        width: 100%;
        height: 1fr;
        padding: 0 1;
    }
    
    #panels {
        width: 100%;
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("1", "strategy_mm", "Market Making", show=False),
        Binding("2", "strategy_mom", "Momentum", show=False),
        Binding("3", "strategy_arb", "Arbitrage", show=False),
        Binding("plus", "speed_up", "Speed Up", show=False),
        Binding("equal", "speed_up", "Speed Up", show=False),
        Binding("minus", "speed_down", "Speed Down", show=False),
        Binding("space", "toggle_pause", "Pause/Resume", show=False),
        Binding("r", "reset_stats", "Reset Stats", show=False),
    ]

    def __init__(self, host: str = "127.0.0.1", port: int = 54321):
        super().__init__()
        self.config = ServerConfig(host=host, port=port)
        self.connection = AsyncTCPConnection(self.config)
        self.generator = OrderGenerator(orders_per_second=100.0)
        self._order_task: asyncio.Task | None = None
        self._stats_task: asyncio.Task | None = None
        self._paused = False
        self._orders_this_second = 0
        self._last_rate_check = 0.0

    def compose(self) -> ComposeResult:
        yield HeaderWidget(self.config.host, self.config.port)
        with Container(id="main-container"):
            with Horizontal(id="panels"):
                yield AlgoPanel()
                yield TapePanel()
                yield TelemetryPanel()
        yield FooterWidget()

    async def on_mount(self):
        self.connection.on_message = self._handle_server_message
        self.connection.on_state_change = self._handle_connection_state
        
        connected = await self.connection.connect()
        header = self.query_one(HeaderWidget)
        header.set_connected(connected)
        
        if connected:
            self._order_task = asyncio.create_task(self._order_loop())
            self._stats_task = asyncio.create_task(self._stats_loop())

    async def on_unmount(self):
        self.connection.on_message = None
        self.connection.on_state_change = None
        if self._order_task:
            self._order_task.cancel()
        if self._stats_task:
            self._stats_task.cancel()
        await self.connection.disconnect()

    def _handle_server_message(self, message: str):
        self.call_later(self._log_tape, message)

    def _log_tape(self, message: str):
        try:
            tape = self.query_one(TapePanel)
            tape.log_message(message)
        except Exception:
            pass

    def _handle_connection_state(self, state: ConnectionState):
        self.call_later(self._update_connection_ui, state)

    def _update_connection_ui(self, state: ConnectionState):
        try:
            header = self.query_one(HeaderWidget)
            header.set_connected(state == ConnectionState.CONNECTED)
        except Exception:
            pass

    async def _order_loop(self):
        import time
        self._last_rate_check = time.time()
        
        while True:
            if self._paused:
                await asyncio.sleep(0.1)
                continue
            
            order = self.generator.generate_one()
            success = await self.connection.send_order(
                order.side.value,
                order.quantity,
                order.price
            )
            
            if success:
                algo = self.query_one(AlgoPanel)
                algo.log_order(order.side_str, order.quantity, order.price)
                self._orders_this_second += 1
            
            await asyncio.sleep(self.generator.delay_between_orders)

    async def _stats_loop(self):
        import time
        
        while True:
            await asyncio.sleep(0.5)
            
            current_time = time.time()
            elapsed = current_time - self._last_rate_check
            
            if elapsed >= 1.0:
                rate = self._orders_this_second / elapsed
                self._orders_this_second = 0
                self._last_rate_check = current_time
            else:
                rate = self._orders_this_second / max(elapsed, 0.1)
            
            telemetry = self.query_one(TelemetryPanel)
            telemetry.update_live_stats(
                self.generator.total_generated,
                self.generator.total_volume,
                rate,
                self.generator.current_strategy.name()
            )

    def action_strategy_mm(self):
        self.generator.set_strategy("market_making")
        self.notify("Strategy: Market Making")

    def action_strategy_mom(self):
        self.generator.set_strategy("momentum")
        self.notify("Strategy: Momentum")

    def action_strategy_arb(self):
        self.generator.set_strategy("arbitrage")
        self.notify("Strategy: Arbitrage")

    def action_speed_up(self):
        new_rate = min(1000.0, self.generator.orders_per_second * 1.5)
        self.generator.set_rate(new_rate)
        self.notify(f"Speed: {new_rate:.0f} orders/sec")

    def action_speed_down(self):
        new_rate = max(1.0, self.generator.orders_per_second / 1.5)
        self.generator.set_rate(new_rate)
        self.notify(f"Speed: {new_rate:.0f} orders/sec")

    def action_toggle_pause(self):
        self._paused = not self._paused
        status = "PAUSED" if self._paused else "RUNNING"
        self.notify(f"Status: {status}")

    def action_reset_stats(self):
        self.generator.reset_stats()
        self.notify("Stats reset")


def run_app(host: str = "127.0.0.1", port: int = 54321):
    app = LobsterApp(host=host, port=port)
    app.run()
