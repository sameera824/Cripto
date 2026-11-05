import asyncio
import json
import os
import redis.asyncio as aioredis
from messaging.schema import AgentSignal


REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL", "agent_signals")


async def publish_signal(signal: AgentSignal) -> None:
    r = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    await r.publish(REDIS_CHANNEL, signal.model_dump_json())
    await r.aclose()


async def subscribe_signals(callback):
    r = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    pubsub = r.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            signal = AgentSignal(**data)
            await callback(signal)
