# Risk Engine & Sub-Agent Specifications (`RISK_AND_AGENTS_SPEC.md`)

Detailed rules for the Central Risk Engine and payload contracts for distributed sub-agents.

---

## 1. Central Risk Engine Specification

The Risk Engine serves as the ultimate gatekeeper on your local device. Every order proposed by sub-agents must pass these validation rules before submission to Binance.

### Risk Rule Matrix

| Rule | Parameter | Description |
|---|---|---|
| **Fixed-Fractional Position Sizing** | `MAX_EQUITY_RISK_PCT = 0.01` | Risk no more than 1% of total portfolio equity on any single trade: `Qty = (Equity * 0.01) / |Entry - StopLoss|`. |
| **Max Daily Loss Limit** | `MAX_DAILY_LOSS_PCT = 0.03` | If realized losses in a 24-hour window reach 3% of starting daily balance, automatically cease opening new positions. |
| **Exchange-Side Stop Loss** | Mandatory | Stop-loss orders must be placed directly on the Binance exchange orderbook alongside position entry. |
| **Exchange Precision Gate** | CCXT `amount_to_precision` / `price_to_precision` | Format all price and quantity floats to exact exchange step-sizes prior to API submission. |
| **Minimum Order Cost Gate** | `limits['cost']['min']` | Reject orders failing Binance's minimum notion value (e.g., < 5 or 10 USDT). |
| **API Error Circuit Breaker** | `MAX_CONSECUTIVE_ERRORS = 5` | Pause trading automatically after 5 consecutive network or API exception errors. |

---

## 2. Sub-Agent Specifications & Payload Contracts

Sub-agents analyze specific market dimensions and send standardized JSON payloads back to the Master Orchestrator.

### Standard Payload Schema (Pydantic / JSON)

```json
{
  "agent_id": "technical_agent_01",
  "timestamp": "2026-11-04T08:35:00Z",
  "symbol": "BTC/USDT",
  "action_signal": "BUY",
  "confidence": 0.85,
  "metrics": {
    "rsi": 28.5,
    "fast_sma": 68200.0,
    "slow_sma": 67900.0
  },
  "suggested_stop_loss": 67500.0,
  "suggested_take_profit": 69500.0,
  "rationale": "Bullish SMA crossover with oversold RSI confirmation"
}
```

### Agent Roles

1. **Technical Analysis Agent (`technical_agent.py`)**:
   - Computes indicators over 5-minute and 1-hour candlestick feeds (RSI, Moving Averages, Donchian Channels).
2. **Sentiment & News Agent (`sentiment_agent.py`)**:
   - Parses news feeds and social media data via LLMs to generate market sentiment scores.
3. **Price Prediction Agent (`predictive_agent.py`)**:
   - Runs short-term price volatility models to output direction probabilities and volatility bounds.
