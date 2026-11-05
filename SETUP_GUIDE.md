# Local Setup & Installation Guide (`SETUP_GUIDE.md`)

Step-by-step instructions for configuring and launching the local Master Node at `/Volumes/HDD/Cripto/`.

---

## 1. Directory Structure Setup

Ensure your local repository at `/Volumes/HDD/Cripto` is organized as follows:

```text
/Volumes/HDD/Cripto/
├── .env                   # Local API keys and broker configs
├── .gitignore             # Git ignore rule file
├── ARCHITECTURE.md        # System architecture documentation
├── SETUP_GUIDE.md         # Local installation instructions
├── RISK_AND_AGENTS_SPEC.md# Strategy & Risk Engine specification
├── AGENTS.md              # VS Code AI Assistant context file
├── master/                # Local Master Node source code
│   ├── main.py            # Master loop & broker listener
│   ├── risk_engine.py     # Risk validation & position sizing
│   └── execution.py       # CCXT Binance connector
├── agents/                # Local/Remote sub-agent scripts
│   ├── technical_agent.py # Technical indicator module
│   ├── sentiment_agent.py # Sentiment/News parser
│   └── predictive_agent.py# Price series predictor
└── messaging/             # Communication schemas
    ├── schema.py          # Pydantic data models
    └── broker.py          # Redis / WebSocket pub-sub client
```

---

## 2. Environment Setup (Python & Dependencies)

Open your terminal, navigate to your workspace, and create a Python virtual environment:

```bash
cd /Volumes/HDD/Cripto

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required core packages
pip install ccxt asyncio pandas numpy pydantic python-dotenv redis websockets
```

---

## 3. Binance Testnet & Environment Configuration

Create a `.env` file at `/Volumes/HDD/Cripto/.env`:

```env
# Binance Testnet Credentials
BINANCE_API_KEY="your_binance_testnet_api_key"
BINANCE_SECRET_KEY="your_binance_testnet_secret_key"
USE_SANDBOX=True

# Message Broker Configuration (Local or Remote Redis)
REDIS_HOST="127.0.0.1"
REDIS_PORT=6379
REDIS_CHANNEL="agent_signals"

# Risk Thresholds
MAX_EQUITY_RISK_PCT=0.01
MAX_DAILY_LOSS_PCT=0.03
```

---

## 4. Launching & Testing

1. **Start Local Redis Broker** (if using Redis):
   ```bash
   docker run -d -p 6379:6379 --name cripto-redis redis:alpine
   ```

2. **Verify Binance Testnet Connectivity**:
   ```bash
   python master/execution.py
   ```

3. **Run Master Orchestrator**:
   ```bash
   python master/main.py
   ```
