import os
import json
import logging
import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import base58
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from typing import Optional, List

# In-memory active wallet storage
saved_wallet = None

class ConfigModel(BaseModel):
    max_daily_loss_sol: float = None
    token_blacklist: list[str] = None
    min_liquidity_sol: float = None
    max_trade_amount_sol: float = None
    slippage_bps: int = None
import aio_pika
import psycopg2
import openai

# FastAPI application
app = FastAPI()
# Serve UI static files (React/Bootstrap dashboard)
app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to UI dashboard."""
    return RedirectResponse(url='/ui')
# Default AI agent configuration (tunable via /config)
config = {
    'max_daily_loss_sol': float(os.getenv('MAX_DAILY_LOSS_SOL', '5.0')),
    'token_blacklist': os.getenv('TOKEN_BLACKLIST', '').split(',') if os.getenv('TOKEN_BLACKLIST') else [],
    'min_liquidity_sol': float(os.getenv('MIN_LIQUIDITY_SOL', '0.1')),
    'max_trade_amount_sol': float(os.getenv('MAX_TRADE_AMOUNT_SOL', '1.0')),
    'slippage_bps': int(os.getenv('JUPITER_SLIPPAGE_BPS', '50'))
}
# Configure startup and shutdown events to manage the consumer
@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    logging.info("Brain starting up: initializing connections")
    # Initialize DB and RabbitMQ connections only; do NOT start consumer until /start
    await init()

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Brain shutting down: stopping consumer and closing connections")
    global consumer_task, rabbit_conn, db_conn
    if consumer_task:
        consumer_task.cancel()
    try:
        if rabbit_conn:
            await rabbit_conn.close()
    except Exception:
        pass
    try:
        if db_conn:
            db_conn.close()
    except Exception:
        pass

# Global state and connections
running = False
consumer_task = None
status = {"positions": [], "pnl": 0, "config": {}}
db_conn = None
rabbit_conn = None
rabbit_channel = None

async def init():
    """Initialize database and RabbitMQ connections."""
    global db_conn, rabbit_conn, rabbit_channel
    database_url = os.getenv('DATABASE_URL')
    rabbit_url = os.getenv('RABBITMQ_URL')
    # Connect to Postgres
    db_conn = psycopg2.connect(database_url)
    # Connect to RabbitMQ
    rabbit_conn = await aio_pika.connect_robust(rabbit_url)
    rabbit_channel = await rabbit_conn.channel()
    # Declare queues
    await rabbit_channel.declare_queue('signals.raw', durable=True)
    await rabbit_channel.declare_queue('signals.decoded', durable=True)

@app.post("/start")
async def start_agent():
    """Start the AI agent consumer."""
    global running, consumer_task
    if running:
        return {"status": "already running"}
    logging.info("Received start command: launching consumer task")
    consumer_task = asyncio.create_task(consume_signals())
    running = True
    return {"status": "started"}

@app.post("/stop")
async def stop_agent():
    """Stop the signal consumer."""
    global running, consumer_task
    if running and consumer_task:
        logging.info("Received stop command: cancelling consumer task")
        consumer_task.cancel()
        running = False
    return {"status": "stopped"}

@app.get("/status")
async def get_status():
    """Return current agent status and running state."""
    return {"running": running, **status}

@app.websocket("/stream")
async def stream(ws: WebSocket):
    """WebSocket endpoint for streaming real-time status."""
    await ws.accept()
    while True:
        await asyncio.sleep(1)
        await ws.send_json({"status": status})
    
@app.get("/config")
async def get_config():
    """Get current AI agent configuration."""
    return config

@app.post("/config")
async def update_config(cfg: ConfigModel):
    """Update AI agent configuration."""
    updated = False
    for field, value in cfg.dict(exclude_unset=True).items():
        if field in config and value is not None:
            config[field] = value
            updated = True
    if not updated:
        raise HTTPException(status_code=400, detail="No valid config fields provided")
    return config

@app.post("/wallet")
async def create_wallet():
    """Generate a new Solana wallet (mnemonic & address)."""
    # Generate BIP39 mnemonic
    mnemo = Mnemonic("english")
    phrase = mnemo.generate(strength=128)
    # Derive seed and Solana key via BIP44
    seed_bytes = Bip39SeedGenerator(phrase).Generate()
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    address = bip44_ctx.PublicKey().ToAddress()
    global saved_wallet
    saved_wallet = {"mnemonic": phrase, "address": address}
    return saved_wallet

class WalletImportModel(BaseModel):
    mnemonic: Optional[str] = None
    secret_key: Optional[List[int]] = None

@app.post("/wallet/import")
async def import_wallet(w: WalletImportModel):
    """Import an existing mnemonic or secret key as the active wallet."""
    global saved_wallet
    # Import via secret key array (64-byte keypair or raw secret) or base58-encoded key
    if w.secret_key is not None:
        sk_bytes = bytes(w.secret_key)
        pub_bytes = sk_bytes[-32:] if len(sk_bytes) >= 32 else sk_bytes
        address = base58.b58encode(pub_bytes).decode('ascii')
        saved_wallet = {"secret_key": w.secret_key, "address": address}
        return saved_wallet
    # If mnemonic provided, determine if phrase or base58
    if w.mnemonic:
        val = w.mnemonic.strip()
        # If spaces present, treat as BIP39 mnemonic
        if ' ' in val:
            try:
                seed_bytes = Bip39SeedGenerator(val).Generate()
                bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
                address = bip44_ctx.PublicKey().ToAddress()
                saved_wallet = {"mnemonic": val, "address": address}
                return saved_wallet
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid mnemonic: {e}")
        # Else treat as Base58-encoded secret key
        try:
            sk_bytes = base58.b58decode(val)
            sk_list = list(sk_bytes)
            pub_bytes = sk_bytes[-32:] if len(sk_bytes) >= 32 else sk_bytes
            address = base58.b58encode(pub_bytes).decode('ascii')
            saved_wallet = {"secret_key": sk_list, "address": address}
            return saved_wallet
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid import key: {e}")
    # No valid import data
    raise HTTPException(status_code=400, detail="No valid wallet import data provided")

@app.get("/wallet")
async def get_wallet():
    """Retrieve the currently active wallet."""
    if saved_wallet:
        return saved_wallet
    raise HTTPException(status_code=404, detail="No wallet generated or imported")

async def consume_signals():
    """Consume signals.raw, batch events, call OpenAI, store & publish decisions."""
    global db_conn, rabbit_channel, status
    # Setup OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')
    # Ensure the raw signals queue is declared
    queue = await rabbit_channel.declare_queue('signals.raw', durable=True)
    buffer = []
    window_start = None

    async with queue.iterator() as it:
        async for message in it:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    logging.info(f"Consumed raw signal: {data.get('type')}")
                except json.JSONDecodeError:
                    logging.error("Invalid JSON in signal")
                    continue
                now = datetime.utcnow()
                if window_start is None:
                    window_start = now
                buffer.append(data)
                # If 30s window passed, process batch
                if (now - window_start).total_seconds() >= 30:
                    # Build prompt
                    pumpfun_events = [e['data'] for e in buffer if e.get('type') == 'pumpfun']
                    raydium_pools = [e['data'] for e in buffer if e.get('type') == 'raydium']
                    twitter_stats = [e['data'] for e in buffer if e.get('type') == 'twitter']
                    prompt = {
                        'portfolio': status,
                        'pumpfun_events': pumpfun_events,
                        'raydium_pools': raydium_pools,
                        'twitter_stats': twitter_stats,
                        'constraints': config
                    }
                    # Call OpenAI
                    try:
                        response = await openai.ChatCompletion.acreate(
                            model='gpt-4o',
                            messages=[
                                {'role': 'system', 'content': 'You are an AI trading agent on Solana.'},
                                {'role': 'user', 'content': json.dumps(prompt)}
                            ],
                            functions=[{
                                'name': 'make_trade',
                                'description': 'Execute trade decision',
                                'parameters': {
                                    'type': 'object',
                                    'properties': {
                                        'action': {'type': 'string', 'enum': ['BUY', 'SELL', 'HOLD']},
                                        'token_mint': {'type': 'string'},
                                        'amount_sol': {'type': 'number'},
                                        'reason': {'type': 'string'}
                                    },
                                    'required': ['action', 'token_mint', 'amount_sol', 'reason']
                                }
                            }],
                            function_call={'name': 'make_trade'}
                        )
                        choice = response.choices[0].message
                        if choice.function_call:
                            args = json.loads(choice.function_call.arguments)
                            decision = args
                        else:
                            decision = {'action': 'HOLD', 'token_mint': '', 'amount_sol': 0, 'reason': 'No action'}
                    except Exception as e:
                        logging.error(f"OpenAI call failed: {e}")
                        decision = {'action': 'HOLD', 'token_mint': '', 'amount_sol': 0, 'reason': 'Error'}
                    # Save decision to DB
                    try:
                        with db_conn.cursor() as cur:
                            cur.execute(
                                "INSERT INTO signals_decoded(decision) VALUES (%s)",
                                (json.dumps(decision),)
                            )
                        db_conn.commit()
                    except Exception as e:
                        logging.error(f"Failed to save decoded signal: {e}")
                    # Publish to decoded queue
                    msg = aio_pika.Message(body=json.dumps(decision).encode())
                    await rabbit_channel.default_exchange.publish(msg, routing_key='signals.decoded')
                    logging.info(f"Published decision: {decision}")
                    # Reset buffer
                    buffer = []
                    window_start = None

def run_consumer():
    asyncio.run(consume_signals())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)