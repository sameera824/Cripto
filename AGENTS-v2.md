# AGENTS-v2.md — VS Code AI Agent Guidance & Multi-Agent Architecture

This document serves as the global context and instruction guide for AI coding agents (e.g., GitHub Copilot, Cursor AI, Roo Code, Windsurf) working on this distributed Binance Multi-Agent Trading Bot repository in VS Code.

---

## 1. Project Directory & Local Root Setup

- **Local Project Path**: `/Volumes/HDD/Cripto`
- **Environment Configuration**: `.env` file located at `/Volumes/HDD/Cripto/.env` containing Binance Testnet API keys and local broker parameters.
- **Recommended Folder Structure**:
  ```text
  /Volumes/HDD/Cripto/
  ├── .env                   # Local API keys (Binance, Redis, etc.)
  ├── .gitignore             # Ignores .env and virtualenv
  ├── AGENTS.md              # AI agent guidelines for VS Code
  ├── master/                # Local Master Node & Risk Engine
  │   ├── main.py            # Entry point for Master Orchestrator
  │   ├── risk_engine.py     # Centralized Risk & Precision Gate
  │   └── execution.py       # CCXT Binance API connector
  ├── agents/                # Distributed Sub-Agent Modules
  │   ├── technical_agent.py # Technical indicators (RSI, SMA)
  │   ├── sentiment_agent.py # Sentiment/LLM news processing
  │   └── predictive_agent.py# Price series prediction
  └── messaging/             # Async communication & broker schemas
      ├── schema.py          # Pydantic models for JSON signals
      └── broker.py          # WebSocket / Redis Pub/Sub client
  ```

---

## 2. System Overview & Core Philosophy

This system is a **decoupled, distributed multi-agent automated crypto trading bot**. 

- **Local Master Node Authority**: The main orchestrator runs strictly on the local device at `/Volumes/HDD/Cripto`, where Binance API credentials and risk validation logic reside.
- **Sub-Agent Isolation**: Specialized analytical sub-agents run across different cloud nodes/platforms and communicate asynchronously with the Master Node.
- **Decoupled Risk Gate**: AI sub-agents **never** execute trades or touch API keys directly. They produce research findings and trade signals. The local Master Program evaluates these signals against a strict **Risk Engine** before sending orders to Binance via CCXT.

---

## 3. System Architecture Layers

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

## 6. Guidelines for AI Coding Assistants in VS Code

When writing or modifying code in this workspace (`/Volumes/HDD/Cripto`):

1. **Language & Environment**:
   - Python 3.12+ using asynchronous programming (`asyncio`, `ccxt.async_support`).
2. **Library Usage**:
   - Use **CCXT / CCXT Pro** for all exchange interactions.
   - Use `pandas` and `numpy` for indicator calculations and backtesting.
3. **Safety & Testnet Default**:
   - Always initialize CCXT in sandbox/testnet mode (`exchange.set_sandbox_mode(True)`) during development and testing.
   - Never hardcode API keys or secrets in source code files. Load secrets strictly from `/Volumes/HDD/Cripto/.env`.
4. **Error Handling**:
   - Implement exponential backoff for network/API reconnection logic.
   - Handle exchange rate limits and CCXT error exceptions (`ccxt.NetworkError`, `ccxt.ExchangeError`).
5. **Code Structure**:
   - Keep strategy logic decoupled from exchange execution logic.
   - Ensure all sub-agent tasks run statelessly so they can restart gracefully without losing conversational or execution context.
