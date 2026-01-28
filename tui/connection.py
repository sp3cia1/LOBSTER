import asyncio
import socket
from dataclasses import dataclass
from typing import Callable, Optional
from enum import Enum


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 54321
    tcp_nodelay: bool = True


class AsyncTCPConnection:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.state = ConnectionState.DISCONNECTED
        self.on_message: Optional[Callable[[str], None]] = None
        self.on_state_change: Optional[Callable[[ConnectionState], None]] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._buffer = ""

    async def connect(self) -> bool:
        self._set_state(ConnectionState.CONNECTING)
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.config.host, self.config.port
            )
            if self.config.tcp_nodelay:
                sock = self.writer.get_extra_info('socket')
                if sock:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._set_state(ConnectionState.CONNECTED)
            self._receive_task = asyncio.create_task(self._receive_loop())
            return True
        except Exception:
            self._set_state(ConnectionState.ERROR)
            return False

    async def disconnect(self):
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass
        self._set_state(ConnectionState.DISCONNECTED)

    async def send_order(self, side: str, quantity: int, price: int) -> bool:
        if self.state != ConnectionState.CONNECTED or not self.writer:
            return False
        try:
            message = f"{side} {quantity} {price}\n"
            self.writer.write(message.encode())
            await self.writer.drain()
            return True
        except Exception:
            self._set_state(ConnectionState.ERROR)
            return False

    async def _receive_loop(self):
        try:
            while self.state == ConnectionState.CONNECTED and self.reader:
                data = await self.reader.read(4096)
                if not data:
                    break
                self._buffer += data.decode()
                while '\n' in self._buffer:
                    line, self._buffer = self._buffer.split('\n', 1)
                    callback = self.on_message
                    if line.strip() and callback:
                        callback(line.strip())
        except asyncio.CancelledError:
            raise
        except Exception:
            self._set_state(ConnectionState.ERROR)

    def _set_state(self, state: ConnectionState):
        self.state = state
        callback = self.on_state_change
        if callback:
            callback(state)

    @property
    def is_connected(self) -> bool:
        return self.state == ConnectionState.CONNECTED
