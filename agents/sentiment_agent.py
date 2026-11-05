import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from messaging.broker import publish_signal
from messaging.schema import AgentSignal

load_dotenv()

SYMBOL = "BTC/USDT"
AGENT_ID = "sentiment_agent_01"
POLL_INTERVAL = 60 * 15  # 15 minutes


def parse_sentiment(text: str) -> tuple[str, float, str]:
    """
    Stub: replace with real LLM inference (e.g. Anthropic Claude API).
    Returns (action_signal, confidence, rationale).
    """
    lower = text.lower()
    bullish_keywords = ["rally", "surge", "bullish", "breakout", "adoption", "inflow"]
    bearish_keywords = ["crash", "dump", "bearish", "hack", "regulation", "selloff"]

    bull_score = sum(1 for kw in bullish_keywords if kw in lower)
    bear_score = sum(1 for kw in bearish_keywords if kw in lower)

    if bull_score > bear_score and bull_score >= 2:
        return "BUY", min(0.5 + bull_score * 0.05, 0.85), f"Bullish sentiment ({bull_score} signals)"
    elif bear_score > bull_score and bear_score >= 2:
        return "SELL", min(0.5 + bear_score * 0.05, 0.85), f"Bearish sentiment ({bear_score} signals)"
    return "NEUTRAL", 0.5, "Neutral/mixed sentiment"


async def fetch_news_text() -> str:
    """
    Stub: replace with a real news API (CryptoPanic, NewsAPI, Twitter/X, etc.).
    Returns aggregated text from recent headlines.
    """
    return "Bitcoin adoption rally expected as institutional inflows surge"


async def run() -> None:
    print(f"[SentimentAgent] Starting. Symbol={SYMBOL}")
    while True:
        raw_text = await fetch_news_text()
        action, confidence, rationale = parse_sentiment(raw_text)

        signal = AgentSignal(
            agent_id=AGENT_ID,
            timestamp=datetime.now(timezone.utc),
            symbol=SYMBOL,
            action_signal=action,
            confidence=confidence,
            metrics={"news_snippet": raw_text[:120]},
            rationale=rationale,
        )

        print(f"[SentimentAgent] {action} | confidence={confidence:.2f} | {rationale}")

        if action != "NEUTRAL":
            await publish_signal(signal)

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run())
