import os
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from messaging.schema import AgentSignal


MAX_EQUITY_RISK_PCT = float(os.getenv("MAX_EQUITY_RISK_PCT", 0.01))
MAX_DAILY_LOSS_PCT = float(os.getenv("MAX_DAILY_LOSS_PCT", 0.03))
MAX_CONSECUTIVE_ERRORS = 5


@dataclass
class RiskState:
    daily_start_balance: float = 0.0
    realized_pnl_today: float = 0.0
    consecutive_errors: int = 0
    trading_halted: bool = False
    last_reset_date: date = field(default_factory=date.today)

    def reset_daily_if_needed(self) -> None:
        today = date.today()
        if today != self.last_reset_date:
            self.realized_pnl_today = 0.0
            self.last_reset_date = today

    def record_error(self) -> None:
        self.consecutive_errors += 1
        if self.consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
            self.trading_halted = True
            print(f"[RiskEngine] Circuit breaker tripped after {MAX_CONSECUTIVE_ERRORS} errors.")

    def clear_errors(self) -> None:
        self.consecutive_errors = 0

    def record_pnl(self, pnl: float) -> None:
        self.reset_daily_if_needed()
        self.realized_pnl_today += pnl
        loss_pct = -self.realized_pnl_today / self.daily_start_balance if self.daily_start_balance else 0
        if loss_pct >= MAX_DAILY_LOSS_PCT:
            self.trading_halted = True
            print(f"[RiskEngine] Daily loss limit {MAX_DAILY_LOSS_PCT*100:.1f}% reached. Trading halted.")


class RiskEngine:
    def __init__(self) -> None:
        self.state = RiskState()

    def set_daily_balance(self, balance: float) -> None:
        self.state.reset_daily_if_needed()
        if self.state.daily_start_balance == 0.0:
            self.state.daily_start_balance = balance

    def validate(
        self,
        signal: AgentSignal,
        equity: float,
        exchange,
    ) -> Optional[dict]:
        """Return order params dict if valid, None if rejected."""
        if self.state.trading_halted:
            print("[RiskEngine] Trading halted — order rejected.")
            return None

        if signal.action_signal == "NEUTRAL":
            return None

        if signal.suggested_stop_loss is None:
            print("[RiskEngine] No stop-loss provided — order rejected.")
            return None

        entry = signal.metrics.get("entry_price")
        if entry is None:
            print("[RiskEngine] No entry_price in metrics — order rejected.")
            return None

        risk_per_unit = abs(entry - signal.suggested_stop_loss)
        if risk_per_unit == 0:
            print("[RiskEngine] Zero risk per unit (entry == stop_loss) — order rejected.")
            return None

        raw_qty = (equity * MAX_EQUITY_RISK_PCT) / risk_per_unit

        market = exchange.market(signal.symbol)
        min_cost = market.get("limits", {}).get("cost", {}).get("min", 0)
        if entry * raw_qty < min_cost:
            print(f"[RiskEngine] Order value below minimum notional {min_cost} — rejected.")
            return None

        qty = float(exchange.amount_to_precision(signal.symbol, raw_qty))
        price = float(exchange.price_to_precision(signal.symbol, entry))
        stop = float(exchange.price_to_precision(signal.symbol, signal.suggested_stop_loss))
        tp = (
            float(exchange.price_to_precision(signal.symbol, signal.suggested_take_profit))
            if signal.suggested_take_profit
            else None
        )

        return {
            "symbol": signal.symbol,
            "side": signal.action_signal.lower(),
            "qty": qty,
            "price": price,
            "stop_loss": stop,
            "take_profit": tp,
        }
