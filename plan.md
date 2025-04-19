Sure. Here's the full rewrite in English:

---

## ✅ Full Development Plan for Autonomous Memecoin AI Agent on Solana

### **Phase 1: Project Setup and Architecture**

1. **Create a private Git repo** with a monorepo structure. Use:
   - **TypeScript/Node.js** for transaction signing and execution (Solana + Jupiter + Pumpfun)
   - **Python** for data collection and AI reasoning
   - **Docker** to connect all services cleanly

2. Define **three main containers**:
   - `collector`: Python + asyncio service that listens to Pump.fun, Raydium, and Twitter.
   - `brain`: Python service that communicates with OpenAI and outputs structured trade decisions.
   - `trader`: Node.js service that signs and sends transactions on Solana.
   - Shared: a PostgreSQL database + RabbitMQ for messaging between services.

3. Use Docker’s internal bridge network. Mount a `secrets/` folder for:
   - The private Solana key
   - OpenAI API key
   - Any config files

---

### **Phase 2: Real-Time Data Collection**

1. In `collector`, install:
   - Twint fork for Twitter scraping
   - Moralis SDK for Pump.fun token data
   - QuickNode Metis client for Raydium pool monitoring
   - WebSocket client for bloXroute’s Pump.fun feed

2. Implement three async tasks:
   - `watch_pumpfun()`: Subscribe to `GetPumpFunNewTokensStream`, store new tokens in `new_tokens` table
   - `watch_raydium()`: Poll `/new-pools` API every 90s, store results in `new_pools`
   - `watch_twitter()`: Run Twint queries for target keywords every 60s, perform sentiment analysis, store in `social_metrics`

3. Publish each event to RabbitMQ queue: `signals.raw`

---

### **Phase 3: The AI Brain (GPT)**

1. In the `brain` container, consume `signals.raw` and group events in 30-second windows.

2. Build a prompt like:
```json
{
  "portfolio": {...},
  "pumpfun_events": [...],
  "raydium_pools": [...],
  "twitter_stats": [...],
  "constraints": {...}
}
```

3. Use OpenAI’s `gpt-4o` model with function calling. Define a function schema like:
```json
{
  "action": "BUY | SELL | HOLD",
  "token_mint": "...",
  "amount_sol": "...",
  "reason": "..."
}
```

4. Validate the response. If invalid, skip or default to `HOLD`.

5. Publish valid decisions to `signals.decoded`

---

### **Phase 4: Trade Execution Engine**

1. `trader` listens to `signals.decoded` queue.

2. Apply trade constraints:
   - Max daily loss
   - Token blacklist
   - Minimum liquidity
   - Position sizing limits

3. If `BUY`:
   - If token is still on bonding curve → use Pumpfun SDK (`pumpfun.buy(mint, amount)`)
   - If tradable via DEX → use Jupiter aggregator API to get route, deserialize transaction, sign, and send

4. If `SELL`: reverse route via Jupiter.

5. After each trade, log result to Postgres (`trades`, `positions` tables).

---

### **Phase 5: Basic User Interface (Optional for Now)**

1. In `brain`, run a small **FastAPI** server with endpoints:
   - `/status`: returns current positions, PnL, and config
   - `/start` and `/stop`: start/stop the AI agent
   - `/stream`: WebSocket for real-time updates

2. Later, build a **Next.js frontend** to consume `/stream` and display:
   - Portfolio value
   - Live trades and decisions
   - Logs of AI reasoning
   - Graphs for profit/loss over time

---

### **Phase 6: Testing and Deployment**

1. **Start on Devnet**:
   - Use dummy wallet, dry-run mode for Jupiter swaps
   - Mock Pumpfun SDK for non-mainnet

2. **Activate Paper Mode**:
   - Sign transactions but do not send them
   - Record PnL hypothetically and observe performance

3. **Move to Mainnet**:
   - Start with 1 SOL test balance
   - Gradually increase as reliability improves

4. **Monitoring**:
   - Add **Grafana + Prometheus** to track:
     - GPT response time
     - Transaction confirmation time
     - PnL curve
     - System heartbeat

5. **Alerts**:
   - Set up Telegram bot for alerts when:
     - Daily loss exceeds threshold
     - Wallet balance too low
     - Any system error occurs

---

## 🧠 Build Instructions for an AI Coding Agent

> **Goal:** Write production-ready code based on the architecture above. Final goal is to launch everything via `docker compose up`.

---

### **1. Repo & Structure**
Create the following:
```text
/
├ collector/         # Python – data ingestion
├ brain/             # Python – OpenAI reasoning
├ trader/            # Node – trading execution
├ database/          # SQL schema + init scripts
├ docker-compose.yml
├ secrets/           # Wallet key, API keys (gitignored)
└ README.md
```

- Use **Poetry** for Python containers and **npm workspaces** for the TypeScript part.

---

### **2. `collector/collector.py`**
- Use `asyncio` and `aiohttp`
- Implement:
   - `watch_pumpfun()` – listens to bloXroute Pump.fun WS
   - `watch_raydium()` – polls QuickNode `/new-pools`
   - `watch_twitter()` – uses Twint, aggregates tweet sentiment
- Insert events into Postgres and publish JSON to RabbitMQ `signals.raw`

---

### **3. `brain/brain.py`**
- Consume messages from `signals.raw`
- Group incoming events, create OpenAI prompt
- Call GPT-4o with `function_call` schema (`make_trade`)
- Parse and validate GPT response
- Post valid trades to `signals.decoded`
- Launch a **FastAPI** server with:
   - `/status`
   - `/start`, `/stop`
   - WebSocket `/stream` pushing decisions in real time

---

### **4. `trader/index.ts`**
- Use:
   - `@solana/web3.js` for signing
   - `@jup-ag/core` for Jupiter swap
   - `pumpfun-sdk` for bonding curve buys

- Consume messages from `signals.decoded`
- Check all risk constraints
- Based on token status:
   - Use Pumpfun SDK if still in bonding phase
   - Use Jupiter aggregator for DEX trades
- Sign and send transactions
- Log results to Postgres (`trades`, `portfolio`)

---

### **5. Docker Compose**
- Each service gets its own Dockerfile:
   - `collector`: Python slim
   - `brain`: Python slim + FastAPI
   - `trader`: Node Alpine
- Use Docker volumes for:
   - `secrets/` (wallet key, API key)
   - `logs/`
- Set up PostgreSQL and RabbitMQ containers

---

### **6. Security**
- Load private key from `secrets/id.json`, do not log it
- Store OpenAI API key in `.env` file inside `secrets/`
- Run containers with minimal permissions (`umask 077`)
- Never expose trade endpoints to the open internet without auth

---

### **7. Testing**
- Write Pytest tests for `collector` and `brain`
- Write Jest tests for `trader`
- Add GitHub Actions CI:
   - Run tests on PR
   - Lint, typecheck
   - Build Docker images

---

### **8. Documentation**
- Fill out README with:
   - Setup instructions
   - Config options (risk, wallet, polling intervals)
   - Start/stop commands
   - Example `.env` and wallet setup
- Add usage guide:
   - How to run in paper mode
   - How to deploy to production VPS

-