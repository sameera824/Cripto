import asyncio
import os
import ccxt.async_support as ccxt
from dotenv import load_dotenv

load_dotenv()

USE_SANDBOX = os.getenv("USE_SANDBOX", "True").lower() == "true"


def build_exchange() -> ccxt.binance:
    exchange = ccxt.binance({
        "apiKey": os.getenv("BINANCE_API_KEY"),
        "secret": os.getenv("BINANCE_SECRET_KEY"),
        "enableRateLimit": True,
    })
    exchange.set_sandbox_mode(USE_SANDBOX)
    return exchange


async def fetch_balance(exchange: ccxt.binance) -> dict:
    balance = await exchange.fetch_balance()
    return balance["total"]


async def place_order(exchange: ccxt.binance, order_params: dict) -> dict:
    symbol = order_params["symbol"]
    side = order_params["side"]
    qty = order_params["qty"]
    price = order_params["price"]
    stop = order_params["stop_loss"]
    tp = order_params.get("take_profit")

    # Entry limit order
    entry_order = await exchange.create_order(
        symbol=symbol,
        type="limit",
        side=side,
        amount=qty,
        price=price,
    )
    print(f"[Execution] Entry order placed: {entry_order['id']}")

    # Stop-loss order (opposite side)
    sl_side = "sell" if side == "buy" else "buy"
    sl_order = await exchange.create_order(
        symbol=symbol,
        type="stop_loss_limit",
        side=sl_side,
        amount=qty,
        price=stop,
        params={"stopPrice": stop},
    )
    print(f"[Execution] Stop-loss order placed: {sl_order['id']}")

    if tp:
        tp_order = await exchange.create_order(
            symbol=symbol,
            type="limit",
            side=sl_side,
            amount=qty,
            price=tp,
        )
        print(f"[Execution] Take-profit order placed: {tp_order['id']}")

    return entry_order


async def verify_connection() -> None:
    exchange = build_exchange()
    try:
        await exchange.load_markets()
        balance = await fetch_balance(exchange)
        usdt = balance.get("USDT", 0)
        print(f"[Execution] Connected to Binance {'Testnet' if USE_SANDBOX else 'Live'}. USDT balance: {usdt}")
    finally:
        await exchange.close()


if __name__ == "__main__":
    asyncio.run(verify_connection())
