Below is a compact “mini‑docs bundle” you can hand straight to any coding‑oriented AI agent.  
Everything is pulled verbatim from the latest public sources as of **17 Apr 2025**, so the agent will not invent non‑existent calls or parameters.

---

## 1. Jupiter V6 Swap API (aggregator)

| Endpoint | Verb | What it returns / expects | Core params |
|----------|------|---------------------------|-------------|
| `/v6/quote` | **GET** | Best route quote (price, route array, fees) | `inputMint`, `outputMint`, `amount` (in minor units), `slippageBps`  citeturn1view0 |
| `/v6/swap` | **POST** | A **base‑64 serialized transaction** ready to sign | Body: `quoteResponse` (from `/quote`), `userPublicKey`, `wrapAndUnwrapSol` (bool), optional `feeAccount` citeturn1view0 |
| `/v6/swap‑instructions` | **POST** | Same as `/swap` but returns raw **instruction objects** so you can compose your own tx | Same body as `/swap` citeturn1view0 |

**Notable flags**

* `asLegacyTransaction=true` forces a legacy tx if the user wallet cannot handle Versioned Transactions. citeturn1view0  
* `excludeDexes=RAYDIUM,SERUM,...` lets you skip AMMs that threw an error in a previous attempt. citeturn1view0  
* `maxAccounts=54` lets you reserve accounts in the tx for extra instructions. citeturn1view0  
* Use `useTokenLedger=true` with `/swap‑instructions` when the exact input amount is only known after a prep instruction. citeturn1view0  

**Minimal TypeScript flow**

```ts
import { Connection, Keypair, VersionedTransaction } from '@solana/web3.js';
import fetch from 'cross-fetch';
import bs58 from 'bs58';

const conn = new Connection('YOUR_RPC');
const wallet = Keypair.fromSecretKey(bs58.decode(process.env.PRIVATE_KEY!));

const quote = await fetch(
  '/v6/quote?inputMint=So111...&outputMint=EPjF...&amount=100000000&slippageBps=50'
).then(r => r.json());

const { swapTransaction } = await fetch('/v6/swap', {
  method: 'POST',
  headers: { 'content-type': 'application/json' },
  body: JSON.stringify({ quoteResponse: quote, userPublicKey: wallet.publicKey.toBase58() })
}).then(r => r.json());

const tx = VersionedTransaction.deserialize(Buffer.from(swapTransaction, 'base64'));
tx.sign([wallet]);
await conn.sendRawTransaction(tx.serialize(), { skipPreflight: true });
```

---

## 2. Raydium resources

### 2.1 QuickNode `/new‑pools` REST endpoint  
*Returns the **200 most recent** Raydium (and Pump.fun) liquidity‑pool launches.*  
* No parameters, paid Metis add‑on required.  
* Response fields: `lpSignature`, `lpAddress`, `tokenAddress`, `quoteAddress`, `lpAmount`, `exchange`, `timestamp`, plus token meta. citeturn7view0  

### 2.2 WebSocket tracking (pure on‑chain)  
QuickNode tutorial shows subscribing to Raydium AMM program (`675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8`) and filtering for the `initialize2` instruction. Code example uses `connection.onLogs()` and parses the mint addresses at index 8 & 9 in the instruction’s account list. citeturn2view0  

### 2.3 Raydium SDK  
`npm i @raydium-io/raydium-sdk` gives typed helpers for AMM math, pool state, token lists, etc. Program IDs and full example snippets (APR calc, farm info parsing) are in the README. citeturn6view0  

---

## 3. Pump.fun data & trading

### 3.1 bloXroute **GetPumpFunNewTokensStream** (WebSocket / gRPC)  
Subscription payload:  
```json
{"jsonrpc":"2.0","id":1,"method":"subscribe",
 "params":["GetPumpFunNewTokensStream",{}]}
```  
Returned fields: `slot`, `txnHash`, `name`, `symbol`, `uri`, `mint`, `bondingCurve`, `creator`, `timestamp`. citeturn4view0  

### 3.2 Moralis **“New Pump.fun Tokens”** REST API  
`GET token/mainnet/exchange/pumpfun/new?limit=100` (header `X-API-Key`).  
Returns array with `tokenAddress`, `name`, `symbol`, `priceNative`, `priceUsd`, `liquidity`, `fullyDilutedValuation`, `createdAt`, etc. Pagination via `cursor`. citeturn5view0  

### 3.3 `@cryptoscan/pumpfun-sdk` (unofficial)  
Install: `npm i @cryptoscan/pumpfun-sdk`. Key methods:  

| Method | What it does | Inputs | Sample |
|--------|--------------|--------|--------|
| `buy()`  | Buy along bonding curve | `wallet`, `coinAddress`, `sol`, optional `slippage`, `priorityFee` | see README buy example citeturn3view0 |
| `sell()` | Sell back to curve | same inputs | see sell example citeturn3view0 |
| `onMint(cb)` | Callback each time **any** new Pump.fun coin is minted | callback receives coin data | citeturn3view0 |
| `waitMint(symbol, cb)` | Wait until a specific symbol launches | `symbol`, callback | citeturn3view0 |

Additional helpers: `listenTransactions`, `listenCoinBump`, `bump`, plus simple SPL transfer helpers.  

---

### How to hand this off

1. Copy‑paste the three sections into the other agent’s context.  
2. Tell it that **all endpoints, parameters, and field names are authoritative** as of 17 Apr 2025.  
3. Instruct it to *only* call what appears here (no guessing new endpoints).  
4. Refer it back to the citations inside each table if it needs fuller prose examples.

That’s everything needed for a grounded, doc‑accurate implementation.


Below is a focused deep‑dive on Pump.fun‑specific APIs and SDKs, ranked by how well they meet the three core needs of your autonomous trading agent:


Need	Ideal feature set
1 — Instant detection of every brand‑new mint	Sub‑second push stream, no polling, high uptime
2 — Fast buying/selling along the bonding curve	Ready‑made signed transactions or SDK helpers
3 — Rich analytics & filtering (price, liquidity, bonding status)	Indexed REST/GraphQL endpoints to enrich GPT prompts
The winning stack combines bloXroute for #1, QuickNode Metis or cryptoscan SDK for #2, and Moralis + Bitquery for #3, with Apify/Helius as low‑code fallbacks.

🚀 Real‑time Mint Streams (Need #1)
bloXroute Trader API
Endpoint: GetPumpFunNewTokensStream (WebSocket/gRPC) delivers every mint with slot, mint, name, symbol, timestamp, etc.  

Latency: tens of milliseconds (runs on pump‑ny & pump‑uk relays).

Authentication: same API key you’d use for Solana MEV or bundle‑submission, so it fits pro trading infra.

Why it’s best: no rate‑limit, production‑grade uptime, already pushes swap streams if you also want trade flow.

Shyft gRPC
A free alternative: subscribe to Pump.fun program address 6EF8r…F6P over gRPC; Node example provided in their blog. 

Good for backup, but requires your own decoding logic and Shyft’s gRPC token.

QuickNode Yellowstone (Geyser)
Their guides show the same pattern and integrate with Metis later on. 

Works, but not as battle‑tested for huge mint floods as bloXroute.

⚡ Execution APIs & SDKs (Need #2)
Option A — QuickNode Metis Pump.fun Swap
Endpoints:

GET /pump-fun/quote → best BUY/SELL quote including cap, supply, status. 

POST /pump-fun/swap and /swap-instructions → ready‑made transaction or raw ix array.

Pros: no custom program logic; you treat it like Jupiter V6. Perfect if you want every trade signed server‑side in TS/Python.

Cons: paid Metis add‑on; only SOL ↔ token (can’t batch or multi‑buy yet).

Option B — @cryptoscan/pumpfun-sdk
NPM package that does buy, sell, transfer, on‑mint, waitMint, bump detector, token sniper out‑of‑the‑box. 

Pure client‑side signing, 0.5 % fee baked into each tx.

You can chain with Jupiter once the token graduates; SDK exposes a simple isGraduated() helper.

Recommended blend:

Use QuickNode Metis for deterministic REST quoting + tx when you need rock‑solid SLAs.

Keep cryptoscan‑SDK as a hot‑path fallback (or for cheaper launch sniping where latency > fee).

📊 Data Enrichment & Filtering (Need #3)

Service	Strengths	Typical GPT input
Moralis Pump.fun API	Single call gets prices, liquidity, metadata, bonding status, OHLCV; includes endpoints getNewPumpfunTokens, getBondingTokens, getGraduatedTokens. 	“Token X market‑cap $75k, still bonding, 220 holders”
Bitquery GraphQL	Deep analytics (buyers/sellers counts, dev wallet, custom market‑cap queries, real‑time subscription). 	“Token Y had 400 unique buyers in last 15 min”
Apify Actors	Low‑code scrapers (New Listings, About‑to‑Graduate, Trade Monitor). Useful if your infra team wants zero on‑chain code. 	
Helius Webhooks	Generic program‑address webhooks; supports Pump.fun logo in docs, so easy to set a webhook on 6EF8r…F6P. 
Helius
🏆 Decision Matrix

Criterion	bloXroute	QuickNode Metis	cryptoscan SDK	Moralis	Bitquery
Latency	★★★★★ <20 ms	★★★★	★★★★	★★ (index delay)	★★
Coverage	New mints	Quote + Swap	Full trade ops	Full lifecycle	Analytics
Cost	Free tier + paid pro	Paid add‑on	0.5 % tx fee	Free ≤ 100 req/s	Free token
Complexity	Stream parse	Simple REST	Import SDK	Simple REST	GraphQL
Adopt: bloXroute for detection, QuickNode/cryptoscan for execution, Moralis + Bitquery for prompt data.

🛠️ Implementation Tips
Detection loop

ts
Copier
Modifier
// pseudo
for (event of bloxroute.onMint()) {
    enqueueToGPT(event)
}
Quote & Buy

ts
Copier
Modifier
const q = await getQuote(mint, 'BUY', solAmount)
if (!q.isCompleted) useQuickNodeSwap(q) else useJupiter()
Data enrichment

python
Copier
Modifier
meta = moralis.get_token_metadata(mint)
stats = bitquery.query(QUERY_BUY_SELL, variables)
feedGPT(meta, stats)
Fallbacks & throttle — if bloXroute key hits limit, auto‑switch to Shyft gRPC; cache Moralis responses for 30‑s to keep API cost down.

That combination satisfies every functional requirement (instant mint alert → AI decision → bonding‑curve buy → price/liq enrichment) without relying on any undocumented Pump.fun internals.