import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from master.execution import build_exchange, fetch_balance, place_order
from master.risk_engine import RiskEngine
from messaging.broker import subscribe_signals
from messaging.schema import AgentSignal

risk_engine = RiskEngine()
pending_signals: list[AgentSignal] = []
MIN_CONFIDENCE = 0.70
MIN_SIGNAL_AGREEMENT = 2  # At least 2 agents must agree on direction


async def on_signal_received(signal: AgentSignal) -> None:
    print(f"[Master] Signal received from {signal.agent_id}: {signal.action_signal} @ {signal.confidence:.2f}")
    pending_signals.append(signal)
    await evaluate_signals()


async def evaluate_signals() -> None:
    if len(pending_signals) < MIN_SIGNAL_AGREEMENT:
        return

    high_conf = [s for s in pending_signals if s.confidence >= MIN_CONFIDENCE]
    if len(high_conf) < MIN_SIGNAL_AGREEMENT:
        return

    buys = [s for s in high_conf if s.action_signal == "BUY"]
    sells = [s for s in high_conf if s.action_signal == "SELL"]

    if len(buys) >= MIN_SIGNAL_AGREEMENT:
        best = max(buys, key=lambda s: s.confidence)
        await execute_signal(best)
        pending_signals.clear()
    elif len(sells) >= MIN_SIGNAL_AGREEMENT:
        best = max(sells, key=lambda s: s.confidence)
        await execute_signal(best)
        pending_signals.clear()


async def execute_signal(signal: AgentSignal) -> None:
    exchange = build_exchange()
    try:
        await exchange.load_markets()
        balance = await fetch_balance(exchange)
        equity = balance.get("USDT", 0)

        risk_engine.set_daily_balance(equity)
        order_params = risk_engine.validate(signal, equity, exchange)

        if order_params is None:
            print("[Master] Signal rejected by Risk Engine.")
            return

        print(f"[Master] Placing {signal.action_signal} order: {order_params}")
        await place_order(exchange, order_params)
        risk_engine.state.clear_errors()

    except Exception as e:
        print(f"[Master] Execution error: {e}")
        risk_engine.state.record_error()
    finally:
        await exchange.close()


async def main() -> None:
    print("[Master] Starting Master Orchestrator...")
    await subscribe_signals(on_signal_received)


if __name__ == "__main__":
    asyncio.run(main())
