import asyncio
import os
from datetime import datetime, timezone
import ccxt.async_support as ccxt
import pandas as pd
from dotenv import load_dotenv

from messaging.broker import publish_signal
from messaging.schema import AgentSignal

load_dotenv()

SYMBOL = "BTC/USDT"
TIMEFRAME = "5m"
RSI_PERIOD = 14
FAST_SMA = 20
SLOW_SMA = 50
AGENT_ID = "technical_agent_01"


def compute_rsi(closes: pd.Series, period: int = 14) -> float:
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])


def compute_sma(closes: pd.Series, window: int) -> float:
    return float(closes.rolling(window).mean().iloc[-1])


def build_signal(df: pd.DataFrame) -> AgentSignal:
    closes = df["close"]
    rsi = compute_rsi(closes, RSI_PERIOD)
    fast = compute_sma(closes, FAST_SMA)
    slow = compute_sma(closes, SLOW_SMA)
    current_price = float(closes.iloc[-1])

    bullish_cross = fast > slow
    oversold = rsi < 35
    overbought = rsi > 65

    if bullish_cross and oversold:
        action = "BUY"
        confidence = min(0.5 + (35 - rsi) / 100, 0.95)
        stop = current_price * 0.985
        tp = current_price * 1.03
        rationale = f"Bullish SMA crossover with oversold RSI ({rsi:.1f})"
    elif not bullish_cross and overbought:
        action = "SELL"
        confidence = min(0.5 + (rsi - 65) / 100, 0.95)
        stop = current_price * 1.015
        tp = current_price * 0.97
        rationale = f"Bearish SMA crossover with overbought RSI ({rsi:.1f})"
    else:
        action = "NEUTRAL"
        confidence = 0.5
        stop = None
        tp = None
        rationale = "No clear signal"

    return AgentSignal(
        agent_id=AGENT_ID,
        timestamp=datetime.now(timezone.utc),
        symbol=SYMBOL,
        action_signal=action,
        confidence=confidence,
        metrics={
            "rsi": round(rsi, 2),
            "fast_sma": round(fast, 2),
            "slow_sma": round(slow, 2),
            "entry_price": current_price,
        },
        suggested_stop_loss=stop,
        suggested_take_profit=tp,
        rationale=rationale,
    )


async def run() -> None:
    exchange = ccxt.binance({"enableRateLimit": True})
    exchange.set_sandbox_mode(os.getenv("USE_SANDBOX", "True").lower() == "true")

    print(f"[TechnicalAgent] Starting. Symbol={SYMBOL} Timeframe={TIMEFRAME}")
    try:
        while True:
            ohlcv = await exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=SLOW_SMA + 10)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

            signal = build_signal(df)
            print(f"[TechnicalAgent] {signal.action_signal} | confidence={signal.confidence:.2f} | {signal.rationale}")

            if signal.action_signal != "NEUTRAL":
                await publish_signal(signal)

            await asyncio.sleep(60 * 5)
    finally:
        await exchange.close()


if __name__ == "__main__":
    asyncio.run(run())
