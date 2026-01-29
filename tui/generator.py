+import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, Optional


class OrderSide(Enum):
    BUY = "B"
    SELL = "S"


@dataclass
class GeneratedOrder:
    side: OrderSide
    quantity: int
    price: int
    timestamp: float

    @property
    def side_str(self) -> str:
        return "BUY" if self.side == OrderSide.BUY else "SELL"


class OrderStrategy(ABC):
    @abstractmethod
    def generate(self) -> GeneratedOrder:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class MarketMakingStrategy(OrderStrategy):
    """Generates orders around a mid-price with aggressive spread crossing"""

    def __init__(
        self,
        mid_price: int = 100,
        spread: int = 2,
        qty_min: int = 10,
        qty_max: int = 500,
        volatility: float = 0.02,
        aggression_rate: int = 5
    ):
        self.mid_price = mid_price
        self.spread = spread
        self.qty_min = qty_min
        self.qty_max = qty_max
        self.volatility = volatility
        self.aggression_rate = aggression_rate
        self._order_count = 0
        self._last_drift_time = time.time()

    def generate(self) -> GeneratedOrder:
        if time.time() - self._last_drift_time > 2.0:
            drift = random.gauss(0, self.mid_price * self.volatility)
            self.mid_price = max(50, min(150, int(self.mid_price + drift)))
            self._last_drift_time = time.time()

        side = OrderSide.BUY if self._order_count % 2 == 0 else OrderSide.SELL
        self._order_count += 1
        
        is_aggressive = (self._order_count % self.aggression_rate == 0)

        if is_aggressive:
            if side == OrderSide.BUY:
                price = self.mid_price + random.randint(1, 3)
            else:
                price = self.mid_price - random.randint(1, 3)
        else:
            if side == OrderSide.BUY:
                price = self.mid_price - random.randint(0, self.spread)
            else:
                price = self.mid_price + random.randint(0, self.spread)

        quantity = random.randint(self.qty_min, self.qty_max)

        return GeneratedOrder(
            side=side,
            quantity=quantity,
            price=price,
            timestamp=time.time()
        )

    def name(self) -> str:
        return "MARKET_MAKING"


class MomentumStrategy(OrderStrategy):
    """Generates orders following momentum with spread crossing"""

    def __init__(self, base_price: int = 100, trend_strength: float = 0.6):
        self.current_price = base_price
        self.trend_strength = trend_strength
        self.trend_direction = 1
        self._steps_in_trend = 0
        self._max_trend_steps = random.randint(10, 30)
        self._order_count = 0

    def generate(self) -> GeneratedOrder:
        self._order_count += 1
        self._steps_in_trend += 1
        
        if self._steps_in_trend >= self._max_trend_steps:
            self.trend_direction *= -1
            self._steps_in_trend = 0
            self._max_trend_steps = random.randint(10, 30)

        if random.random() < self.trend_strength:
            self.current_price += self.trend_direction
            self.current_price = max(50, min(150, self.current_price))

        side = OrderSide.BUY if self.trend_direction > 0 else OrderSide.SELL
        
        is_aggressive = (self._order_count % 4 == 0)
        if is_aggressive:
            side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
        elif random.random() < 0.2:
            side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY

        quantity = random.randint(50, 200)

        return GeneratedOrder(
            side=side,
            quantity=quantity,
            price=self.current_price,
            timestamp=time.time()
        )

    def name(self) -> str:
        return "MOMENTUM"


class ArbitrageStrategy(OrderStrategy):
    """Aggressive spread-crossing for maximum trade execution"""

    def __init__(self):
        self.mid_price = 100
        self._index = 0

    def generate(self) -> GeneratedOrder:
        self._index += 1
        side = OrderSide.BUY if self._index % 2 == 0 else OrderSide.SELL
        
        if side == OrderSide.BUY:
            price = self.mid_price + random.randint(0, 2)
        else:
            price = self.mid_price - random.randint(0, 2)
        
        if self._index % 20 == 0:
            self.mid_price += random.randint(-2, 2)
            self.mid_price = max(90, min(110, self.mid_price))

        return GeneratedOrder(
            side=side,
            quantity=random.randint(100, 500),
            price=price,
            timestamp=time.time()
        )

    def name(self) -> str:
        return "ARBITRAGE"


class OrderGenerator:
    """Main order generator that can switch between strategies"""

    def __init__(self, orders_per_second: float = 100.0):
        self.orders_per_second = orders_per_second
        self.strategies = {
            "market_making": MarketMakingStrategy(),
            "momentum": MomentumStrategy(),
            "arbitrage": ArbitrageStrategy()
        }
        self.current_strategy_name = "market_making"
        self.total_generated = 0
        self.total_volume = 0
        self._running = False

    @property
    def current_strategy(self) -> OrderStrategy:
        return self.strategies[self.current_strategy_name]

    def set_strategy(self, name: str):
        if name in self.strategies:
            self.current_strategy_name = name

    def set_rate(self, orders_per_second: float):
        self.orders_per_second = max(1.0, min(1000.0, orders_per_second))

    def generate_one(self) -> GeneratedOrder:
        order = self.current_strategy.generate()
        self.total_generated += 1
        self.total_volume += order.quantity
        return order

    @property
    def delay_between_orders(self) -> float:
        return 1.0 / self.orders_per_second

    def reset_stats(self):
        self.total_generated = 0
        self.total_volume = 0
