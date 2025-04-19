import fs from 'fs';
import amqplib from 'amqplib';
import { Connection, Keypair, VersionedTransaction } from '@solana/web3.js';
import type { AxiosStatic } from 'axios';
import _axios from 'axios';
import { PumpApi } from '@cryptoscan/pumpfun-sdk';
import pkg from 'pg';
const { Pool } = pkg;

const axios = _axios as unknown as AxiosStatic;

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://localhost';
const DATABASE_URL = process.env.DATABASE_URL || '';
const SOLANA_KEYPAIR_PATH = process.env.SOLANA_KEYPAIR_PATH || '';
// Risk constraints
const TOKEN_BLACKLIST = process.env.TOKEN_BLACKLIST ? process.env.TOKEN_BLACKLIST.split(',') : [];
const MAX_TRADE_AMOUNT_SOL = parseFloat(process.env.MAX_TRADE_AMOUNT_SOL || '1.0');
const SOLANA_CLUSTER_URL = process.env.SOLANA_CLUSTER_URL || 'https://api.mainnet-beta.solana.com';

async function main() {
  // Initialize RabbitMQ
  const mqConn = await amqplib.connect(RABBITMQ_URL);
  const channel = await mqConn.createChannel();
  await channel.assertQueue('signals.decoded', { durable: true });

  // Initialize Postgres
  const pool = new Pool({ connectionString: DATABASE_URL });

  // Load Solana keypair
  const keypairData = JSON.parse(fs.readFileSync(SOLANA_KEYPAIR_PATH, 'utf8'));
  const secret = Uint8Array.from(keypairData);
  const keypair = Keypair.fromSecretKey(secret);
  const connection = new Connection(SOLANA_CLUSTER_URL);

  // Initialize SDKs
  const pumpfun = new PumpApi({ connection });
  const JUPITER_API_URL = process.env.JUPITER_API_URL || 'https://quote-api.jup.ag';
  const JUPITER_SLIPPAGE_BPS = parseInt(process.env.JUPITER_SLIPPAGE_BPS || '50');
const SOL_MINT = 'So11111111111111111111111111111111111111112';
// Liquidity constraint
const MIN_LIQUIDITY_SOL = parseFloat(process.env.MIN_LIQUIDITY_SOL || '0.1');

  console.log('Trader listening for decisions...');
  channel.consume(
    'signals.decoded',
    async (msg) => {
      if (!msg) return;
      let decision;
      try {
        decision = JSON.parse(msg.content.toString());
      } catch (e) {
        console.error('Invalid decision JSON', e);
        channel.ack(msg);
        return;
      }
      console.log('Received decision', decision);
      // Apply risk constraints
      if (TOKEN_BLACKLIST.includes(decision.token_mint)) {
        console.log(`Token ${decision.token_mint} is blacklisted; skipping trade.`);
        channel.ack(msg);
        return;
      }
      if (decision.amount_sol > MAX_TRADE_AMOUNT_SOL) {
        console.log(`Trade amount ${decision.amount_sol} SOL exceeds max allowed ${MAX_TRADE_AMOUNT_SOL}; skipping trade.`);
        channel.ack(msg);
        return;
      }
      // Check minimum liquidity
      try {
        const liqRes = await pool.query(
          `SELECT pool_data->>'lpAmount' as liq FROM new_pools WHERE pool_data->>'tokenAddress' = $1 ORDER BY created_at DESC LIMIT 1`,
          [decision.token_mint]
        );
        const liq = liqRes.rowCount ? parseFloat(liqRes.rows[0].liq) : 0;
        if (liq < MIN_LIQUIDITY_SOL) {
          console.log(`Liquidity ${liq} below min ${MIN_LIQUIDITY_SOL}; skipping trade.`);
          channel.ack(msg);
          return;
        }
      } catch (e) {
        console.error('Liquidity check failed', e);
      }

      // Execute trade based on action
      const action = decision.action;
      if (action === 'BUY') {
        try {
          // Determine if token is still on bonding curve
          const res = await pool.query(
            'SELECT raw_data FROM new_tokens WHERE token_mint = $1 ORDER BY created_at DESC LIMIT 1',
            [decision.token_mint]
          );
          const row = res.rows[0];
          if (row && row.raw_data && row.raw_data.bondingCurve) {
            // Pumpfun bonding-curve buy
            const txid = await pumpfun.buy({ wallet: keypair, coinAddress: decision.token_mint, sol: decision.amount_sol });
            console.log('Pumpfun BUY txid', txid);
            decision.txid = txid;
          } else {
            // DEX buy via Jupiter REST API
            const amount = Math.round(decision.amount_sol * 1e9);
            // Quote
            const quoteResp = await axios.get(`${JUPITER_API_URL}/v6/quote`, {
              params: {
                inputMint: SOL_MINT,
                outputMint: decision.token_mint,
                amount,
                slippageBps: JUPITER_SLIPPAGE_BPS
              }
            });
            const quote = quoteResp.data;
            // Swap
            const swapResp = await axios.post(
              `${JUPITER_API_URL}/v6/swap`,
              {
                quoteResponse: quote,
                userPublicKey: keypair.publicKey.toBase58(),
                wrapAndUnwrapSol: false
              }
            );
            const swapTxB64 = swapResp.data.swapTransaction;
            const tx = VersionedTransaction.deserialize(Buffer.from(swapTxB64, 'base64'));
            tx.sign([keypair]);
            const txid = await connection.sendRawTransaction(tx.serialize(), { skipPreflight: false });
            console.log('DEX BUY txid', txid);
            decision.txid = txid;
          }
        } catch (e: any) {
          console.error('BUY execution failed', e);
          decision.error = e.toString();
        }
      } else if (action === 'SELL') {
        try {
          // Determine if token is still on bonding curve
          const res = await pool.query(
            'SELECT raw_data FROM new_tokens WHERE token_mint = $1 ORDER BY created_at DESC LIMIT 1',
            [decision.token_mint]
          );
          const row = res.rows[0];
          if (row && row.raw_data && row.raw_data.bondingCurve) {
             // Pumpfun bonding-curve sell
             // NOTE: Assuming decision.amount_sol here represents the amount *of the token* to sell, denominated in SOL equivalent.
             // The SDK might require the actual token amount. Verify this if selling fails.
            const txid = await pumpfun.sell({ wallet: keypair, coinAddress: decision.token_mint, sol: decision.amount_sol });
            console.log('Pumpfun SELL txid', txid);
            decision.txid = txid;
          } else {
            // DEX sell via Jupiter REST API
            const amount = Math.round(decision.amount_sol * 1e9); // Assuming amount_sol here is SOL value equivalent to sell
            // TODO: This amount logic might be incorrect for SELL.
            // Usually, for selling a token, you specify the *token amount*, not the SOL equivalent.
            // Need to confirm how the 'decision.amount_sol' is determined by the 'brain'.
            // If it's the SOL value, we might need the token balance first to calculate the token amount.

            // Quote reverse
            const quoteResp = await axios.get(`${JUPITER_API_URL}/v6/quote`, {
              params: {
                inputMint: decision.token_mint,
                outputMint: SOL_MINT,
                amount, // This 'amount' needs clarification - is it token amount or SOL value?
                slippageBps: JUPITER_SLIPPAGE_BPS
              }
            });
            const quote = quoteResp.data;
            // Swap
            const swapResp = await axios.post(
              `${JUPITER_API_URL}/v6/swap`,
              {
                quoteResponse: quote,
                userPublicKey: keypair.publicKey.toBase58(),
                wrapAndUnwrapSol: false
              }
            );
            const swapTxB64 = swapResp.data.swapTransaction;
            const tx = VersionedTransaction.deserialize(Buffer.from(swapTxB64, 'base64'));
            tx.sign([keypair]);
            const txid = await connection.sendRawTransaction(tx.serialize(), { skipPreflight: false });
            console.log('DEX SELL txid', txid);
            decision.txid = txid;
          }
        } catch (e: any) {
          console.error('SELL execution failed', e);
          decision.error = e.toString();
        }
      } else {
        console.log('HOLD - no trade executed');
      }

      // Log trade result to Postgres
      try {
        await pool.query('INSERT INTO trades(trade) VALUES($1)', [decision]);
      } catch (e) {
        console.error('DB insert trade failed', e);
      }
      channel.ack(msg);
    },
    { noAck: false }
  );
}

main().catch(console.error);