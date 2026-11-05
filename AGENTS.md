# AGENTS.md — VS Code AI Agent Guidance & Multi-Agent Architecture

This document serves as the global context and instruction guide for AI coding agents (e.g., GitHub Copilot, Cursor AI, Roo Code, Windsurf) working on this distributed Binance Multi-Agent Trading Bot repository in VS Code.

---

## 1. System Overview & Core Philosophy

This system is a **decoupled, distributed multi-agent automated crypto trading bot**. 

- **Local Master Node Authority**: The main orchestrator runs strictly on the local device where Binance API credentials and risk validation logic reside.
- **Sub-Agent Isolation**: Specialized analytical sub-agents run across different cloud nodes/platforms and communicate asynchronously with the Master Node.
- **Decoupled Risk Gate**: AI sub-agents **never** execute trades or touch API keys directly. They produce research findings and trade signals. The local Master Program evaluates these signals against a strict **Risk Engine** before sending orders to Binance via CCXT.

---

## 2. System Architecture Layers

The architecture is divided into 5 independent, testable layers:

1. **Data Ingestion Layer**: 
   - Historical candle data via REST API.
   - Real-time streaming price tickers and depth order books via WebSockets (`ccxt.pro`).
2. **Sub-Agent Layer (Distributed Analysis)**:
   - Independent specialized agents running on cloud/remote environments (AWS, GCP, local).
3. **Communication Layer**:
   - Asynchronous messaging broker (Redis Pub/Sub, WebSockets, or gRPC) using JSON payload schemas.
4. **Master Decision & Risk Engine (Local)**:
   - Aggregates sub-agent signals, applies weighted consensus/voting, and checks account balance, maximum daily drawdown, and position limits.
5. **Execution Layer (Binance API)**:
   - Submits limit/market orders with price and quantity precision handling via CCXT.

---

## 3. Specialized AI Agent Roles & Specifications

### 🤖 Agent 1: Technical Analysis Agent (`technical_agent.py`)
- **Primary Goal**: Compute technical indicators and market structure signals.
- **Key Indicators**: RSI, Moving Average Crossovers (SMA/EMA), Donchian Breakouts, and Order Book Spread/Imbalance.
- **Output**: JSON signal (`BUY`, `SELL`, `NEUTRAL`) with confidence score (`0.0 - 1.0`).

### 🤖 Agent 2: Sentiment & News Agent (`sentiment_agent.py`)
- **Primary Goal**: Analyze crypto news feeds, social sentiment, and macro market announcements using LLM inference.
- **Output**: JSON payload indicating sentiment polarity, market risk factors, and momentum signals.

### 🤖 Agent 3: Price Prediction Agent (`predictive_agent.py`)
- **Primary Goal**: Process time-series data to predict short-term price volatility and trend probabilities.
- **Output**: Directional forecast and target stop/take-profit levels.

### 👑 Local Master Orchestrator & Risk Gate (`master_orchestrator.py`)
- **Primary Goal**: Receive sub-agent payloads, aggregate findings into a trading decision, validate via Risk Engine, and submit orders via CCXT.
- **API Security**: Local `.env` credential management; zero network exposure of private keys to sub-agents.
- **Risk Gate Enforcement**:
  - Maximum 1% equity risk per trade.
  - Mandatory exchange-side stop-loss and take-profit orders.
  - Daily loss limit threshold and automatic API error circuit breaker (kill-switch).
  - Price and amount precision formatting (`amount_to_precision`, `price_to_precision`).

---

## 4. Communication Protocol & JSON Payload Schema

All sub-agents must publish findings to the message broker using the following standardized JSON format:

```json
{
  "agent_id": "technical_agent_01",
  "timestamp": "2026-11-04T08:25:00Z",
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
  "rationale": "Oversold RSI combined with bullish SMA crossover"
}
```

---

## 5. Guidelines for AI Coding Assistants in VS Code

When writing or modifying code in this workspace:

1. **Language & Environment**:
   - Python 3.12+ using asynchronous programming (`asyncio`, `ccxt.async_support`).
2. **Library Usage**:
   - Use **CCXT / CCXT Pro** for all exchange interactions.
   - Use `pandas` and `numpy` for indicator calculations and backtesting.
3. **Safety & Testnet Default**:
   - Always initialize CCXT in sandbox/testnet mode (`exchange.set_sandbox_mode(True)`) during development and testing.
   - Never hardcode API keys or secrets in source code files. Use `os.getenv()` or `pydantic-settings`.
4. **Error Handling**:
   - Implement exponential backoff for network/API reconnection logic.
   - Handle exchange rate limits and CCXT error exceptions (`ccxt.NetworkError`, `ccxt.ExchangeError`).
5. **Code Structure**:
   - Keep strategy logic decoupled from the exchange execution logic.
   - Ensure all sub-agent tasks run statelessly so they can restart gracefully without losing conversational or execution context.
