import asyncio
import os
import json
import logging
from datetime import datetime
import aiohttp
import aio_pika
import psycopg2
import snscrape.modules.twitter as sntwitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Collector:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.rabbit_url = os.getenv("RABBITMQ_URL")
        self.pumpfun_ws_url = os.getenv("PUMPFUN_WS_URL")
        self.raydium_pools_url = os.getenv("RAYDIUM_POOLS_URL")
        self.twitter_keywords = os.getenv("TWITTER_KEYWORDS", "")
        self.twitter_interval = int(os.getenv("TWITTER_POLL_INTERVAL", "60"))
        self.loop = asyncio.get_event_loop()
        self.rabbit_conn = None
        self.rabbit_channel = None
        self.analyzer = SentimentIntensityAnalyzer()

    async def init(self):
        # Initialize RabbitMQ connection
        self.rabbit_conn = await aio_pika.connect_robust(self.rabbit_url)
        self.rabbit_channel = await self.rabbit_conn.channel()
        await self.rabbit_channel.declare_queue('signals.raw', durable=True)

    async def publish_signal(self, signal: dict):
        msg = aio_pika.Message(body=json.dumps(signal).encode())
        await self.rabbit_channel.default_exchange.publish(msg, routing_key='signals.raw')

    def save_new_tokens(self, data: dict):
        try:
            conn = psycopg2.connect(self.db_url)
            token_mint = data.get('tokenMint') or data.get('mint') or ''
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO new_tokens(token_mint, raw_data) VALUES (%s, %s)",
                    (token_mint, json.dumps(data))
                )
                conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to insert new token: {e}")

    def save_new_pools(self, data: dict):
        try:
            conn = psycopg2.connect(self.db_url)
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO new_pools(pool_data) VALUES (%s)",
                    (json.dumps(data),)
                )
                conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to insert new pool: {e}")

    def save_social_metrics(self, data: dict):
        try:
            conn = psycopg2.connect(self.db_url)
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO social_metrics(metrics) VALUES (%s)",
                    (json.dumps(data),)
                )
                conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Failed to insert social metric: {e}")

    async def watch_pumpfun(self):
        logging.info("Starting watch_pumpfun")
        # Continuously connect and listen, with reconnection logic
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(self.pumpfun_ws_url) as ws:
                        logging.info("Connected to Pump.fun WebSocket")
                        # Subscribe to PumpFun stream
                        subscribe_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "subscribe",
                            "params": ["GetPumpFunNewTokensStream", {}]
                        }
                        await ws.send_json(subscribe_payload)
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                try:
                                    raw = json.loads(msg.data)
                                    # Extract actual event payload
                                    data = raw.get('params', {}).get('result', raw)
                                    # Log pumpfun event
                                    mint = data.get('mint') or data.get('tokenMint')
                                    logging.info(f"Pumpfun event received: mint={mint}")
                                except Exception:
                                    logging.error("Invalid JSON from pumpfun WebSocket")
                                    continue
                                # Save to DB and publish
                                self.loop.run_in_executor(None, self.save_new_tokens, data)
                                await self.publish_signal({"type": "pumpfun", "data": data})
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                logging.error("Pumpfun WS error, reconnecting")
                                break
            except Exception as e:
                logging.error(f"Pumpfun WebSocket connection failed: {e}")
            # Wait before reconnect attempt
            await asyncio.sleep(5)

    async def watch_raydium(self):
        logging.info("Starting watch_raydium")
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    resp = await session.get(self.raydium_pools_url)
                    data = await resp.json()
                    # Assume data is a list of pools
                    for pool in data:
                        # Log raydium pool event
                        logging.info(f"Raydium new pool: {pool.get('id') or pool.get('address')}")
                        self.loop.run_in_executor(None, self.save_new_pools, pool)
                        await self.publish_signal({"type": "raydium", "data": pool})
                except Exception as e:
                    logging.error(f"Error polling raydium: {e}")
                await asyncio.sleep(90)

    def fetch_twitter_metrics(self, since):
        """Synchronous scrape of Twitter keywords since a given time."""
        metrics = []
        for keyword in self.twitter_keywords.split(','):
            keyword = keyword.strip()
            count = 0
            sentiment_total = 0.0
            # Limit to max 100 tweets
            for tweet in sntwitter.TwitterSearchScraper(keyword).get_items():
                if tweet.date < since or count >= 100:
                    break
                count += 1
                score = self.analyzer.polarity_scores(tweet.content)['compound']
                sentiment_total += score
            avg_sentiment = sentiment_total / count if count > 0 else 0.0
            metrics.append({'keyword': keyword, 'count': count, 'avg_sentiment': avg_sentiment, 'since': since.isoformat()})
        return metrics

    async def watch_twitter(self):
        logging.info("Starting watch_twitter")
        prev_time = datetime.utcnow()
        while True:
            now = datetime.utcnow()
            try:
                metrics_list = await self.loop.run_in_executor(None, self.fetch_twitter_metrics, prev_time)
                for metric in metrics_list:
                    # Save and publish each metric
                    await self.loop.run_in_executor(None, self.save_social_metrics, metric)
                    await self.publish_signal({'type': 'twitter', 'data': metric})
            except Exception as e:
                logging.error(f"Error in watch_twitter: {e}")
            prev_time = now
            await asyncio.sleep(self.twitter_interval)

async def main():
    logging.basicConfig(level=logging.INFO)
    collector = Collector()
    await collector.init()
    tasks = [
        asyncio.create_task(collector.watch_pumpfun()),
        asyncio.create_task(collector.watch_raydium()),
        # asyncio.create_task(collector.watch_twitter()) # Disabled twitter for now due to SSL errors
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
