# Autonomous Memecoin AI Agent on Solana

This repository contains an autonomous trading system for Solana memecoins, powered by real-time data collection, OpenAI reasoning, and automated trade execution.

Directories:
  * collector/  - Python service collecting real-time data (Pump.fun, Raydium, Twitter)
  * brain/      - Python OpenAI reasoning service with FastAPI UI
  * trader/     - Node.js trading execution service (Solana, Jupiter, Pumpfun)
  * database/   - SQL schema initialization scripts
  * secrets/    - Secret files (wallet key, API keys) [gitignored]

Key files:
  * docker-compose.yml - Orchestrates services: PostgreSQL, RabbitMQ, collector, brain, trader
  * .gitignore          - Specifies untracked files and directories

Prerequisites:
  * Docker & Docker Compose
  * (Optional) Python 3.9 & Poetry for local development
  * (Optional) Node.js & npm for local development

Setup:
1. Copy secrets:
   ```bash
   mkdir -p secrets
   cp secrets/.env.example secrets/.env
   # Place your Solana keypair file at secrets/id.json
   ```
2. Build and start all services:
   ```bash
   docker-compose up --build
   ```
3. Access services:
   - RabbitMQ UI: http://localhost:15672 (guest/guest)
   - Brain API: http://localhost:8000

Local Development:
- collector:
  ```bash
  cd collector
  poetry install
  poetry run python collector.py
  ```
- brain:
  ```bash
  cd brain
  poetry install
  poetry run uvicorn brain:app --reload --port 8000
  ```
- trader:
  ```bash
  cd trader
  npm install
  npm start
  ```

Testing:
```bash
# Collector and brain (Python)
cd collector && pytest
cd brain && pytest

# Trader (Node.js)
cd trader && npm test
```

CI:
Has GitHub Actions workflows for testing, linting, and building Docker images (.github/workflows/ci.yml).

Refer to plan.md for detailed architecture and implementation plan.
Brain Service API Endpoints:
  * GET  /status   - Current positions, PnL
  * POST /start    - Start the AI agent
  * POST /stop     - Stop the AI agent
  * GET  /stream   - WebSocket stream of real-time status
  * GET  /config   - View or retrieve AI agent configuration (risk, slippage, etc.)
  * POST /config   - Update AI agent configuration. JSON body may include:
      - max_daily_loss_sol: float
      - token_blacklist: array of token mint strings
      - min_liquidity_sol: float
      - max_trade_amount_sol: float
      - slippage_bps: integer
  * POST /wallet   - Generate a new Solana wallet; returns a JSON payload with mnemonic and address