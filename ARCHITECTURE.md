# System Architecture & Data Flow (`ARCHITECTURE.md`)

This document outlines the distributed architecture for the Binance Multi-Agent Trading Bot system.

---

## 1. High-Level Architecture Overview

The system uses a **decoupled, event-driven microservice architecture**. Specialized sub-agents run across different compute environments and platforms, producing analytical signals asynchronously. The **Local Master Node** acts as the central authority on your local device (`/Volumes/HDD/Cripto`), receiving sub-agent findings, aggregating decision signals, validating trades against a strict Risk Engine, and executing orders via Binance API.

```
       +-------------------------------------------------------+
       |             Remote Cloud & External Compute           |
       |                                                       |
       |  +------------------+        +---------------------+  |
       |  | Technical Agent  |        |  Sentiment Agent    |  |
       |  +--------+---------+        +----------+----------+  |
       |           |                             |             |
       |           +--------------+--------------+             |
       |                          |                            |
       +--------------------------|----------------------------+
                                  | Asynchronous Payload (JSON)
                                  v
       +-------------------------------------------------------+
       |             Local Device (/Volumes/HDD/Cripto)       |
       |                                                       |
       |               +----------------------+                |
       |               | Message Broker/Inbox |                |
       |               +----------+-----------+                |
       |                          |                            |
       |                          v                            |
       |              +------------------------+               |
       |              | Master Orchestrator    |               |
       |              +-----------+------------+               |
       |                          |                            |
       |                          v                            |
       |              +------------------------+               |
       |              |   Central Risk Engine  |               |
       |              +-----------+------------+               |
       |                          | Validated Orders           |
       |                          v                            |
       |              +------------------------+               |
       |              |  CCXT / Binance API    |               |
       |              +------------------------+               |
       +-------------------------------------------------------+
```

---

## 2. The 5 Core System Layers

1. **Market Data Streamer**: Fetches real-time price tickers, order books, and candlestick OHLCV data using CCXT / WebSockets.
2. **Sub-Agent Analysis Fleet**: Independent analytical workers evaluating market structure, technical indicators, news sentiment, and short-term price dynamics.
3. **Async Communication Mesh**: Asynchronous pub/sub broker (Redis or WebSockets) handling cross-platform message routing.
4. **Master Decision & Risk Gate**: Evaluates incoming signals, calculates weighted consensus, checks position limits and daily loss thresholds.
5. **Exchange Order Execution**: Formats prices and quantities according to Binance precision rules and submits live/testnet limit or market orders.

---

## 3. Security Boundaries & API Hygiene

- **Zero Remote Key Exposure**: Binance API keys (`BINANCE_API_KEY`, `BINANCE_SECRET_KEY`) reside exclusively in local environment files (`/Volumes/HDD/Cripto/.env`) and are never transmitted to remote sub-agents.
- **Restricted API Permissions**: Enable Spot/Futures Trading, bind IP whitelisting to your local device, and **disable withdrawal permissions**.
- **Stateless Sub-Agents**: Remote sub-agents operate statelessly; if a cloud instance restarts, the local Master Node continues operating without interruption.
