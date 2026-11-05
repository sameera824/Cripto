import asyncio
import os
from datetime import datetime, timezone
import ccxt.async_support as ccxt
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from messaging.broker import publish_signal
from messaging.schema import AgentSignal

load_dotenv()

SYMBOL = "BTC/USDT"
TIMEFRAME = "1h"
LOOKBACK = 48
AGENT_ID = "predictive_agent_01"
POLL_INTERVAL = 60 * 60  # 1 hour


def predict_direction(df: pd.DataFrame) -> tuple[str, float, float, float, str]:
    """
    Simple momentum + volatility model.
    Returns (action_signal, confidence, stop_loss, take_profit, rationale).
    Replace with a proper time-series model (LSTM, Prophet, etc.) for production.
    """
    closes = df["close"].values.astype(float)
    current = closes[-1]

    returns = np.diff(closes) / closes[:-1]
    volatility = float(np.std(returns) * np.sqrt(24))
    momentum = float((closes[-1] - closes[-8]) / closes[-8])

    atr = float(df["high"].sub(df["low"]).rolling(14).mean().iloc[-1])

    if momentum > 0.01 and volatility < 0.05:
        action = "BUY"
        confidence = min(0.55 + momentum * 10, 0.90)
        stop = current - 1.5 * atr
        tp = current + 2.5 * atr
        rationale = f"Positive momentum {momentum*100:.2f}% with low volatility {volatility*100:.2f}%"
    elif momentum < -0.01 and volatility < 0.05:
        action = "SELL"
        confidence = min(0.55 + abs(momentum) * 10, 0.90)
        stop = current + 1.5 * atr
        tp = current - 2.5 * atr
        rationale = f"Negative momentum {momentum*100:.2f}% with low volatility {volatility*100:.2f}%"
    else:
        action = "NEUTRAL"
        confidence = 0.5
        stop = current - atr
        tp = current + atr
        rationale = f"High volatility {volatility*100:.2f}% or weak momentum"

    return action, confidence, stop, tp, rationale


async def run() -> None:
    exchange = ccxt.binance({"enableRateLimit": True})
    exchange.set_sandbox_mode(os.getenv("USE_SANDBOX", "True").lower() == "true")

    print(f"[PredictiveAgent] Starting. Symbol={SYMBOL} Timeframe={TIMEFRAME}")
    try:
        while True:
            ohlcv = await exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=LOOKBACK + 10)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            current_price = float(df["close"].iloc[-1])

            action, confidence, stop, tp, rationale = predict_direction(df)

            signal = AgentSignal(
                agent_id=AGENT_ID,
                timestamp=datetime.now(timezone.utc),
                symbol=SYMBOL,
                action_signal=action,
                confidence=confidence,
                metrics={
                    "entry_price": current_price,
                    "timeframe": TIMEFRAME,
                },
                suggested_stop_loss=stop,
                suggested_take_profit=tp,
                rationale=rationale,
            )

            print(f"[PredictiveAgent] {action} | confidence={confidence:.2f} | {rationale}")

            if action != "NEUTRAL":
                await publish_signal(signal)

            await asyncio.sleep(POLL_INTERVAL)
    finally:
        await exchange.close()


if __name__ == "__main__":
    asyncio.run(run())
