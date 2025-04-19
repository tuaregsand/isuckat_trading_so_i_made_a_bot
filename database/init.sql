-- Database initialization for Autonomous Memecoin AI Agent
CREATE TABLE IF NOT EXISTS new_tokens (
    id SERIAL PRIMARY KEY,
    token_mint TEXT NOT NULL,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS new_pools (
    id SERIAL PRIMARY KEY,
    pool_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS social_metrics (
    id SERIAL PRIMARY KEY,
    metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signals_raw (
    id SERIAL PRIMARY KEY,
    signal JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS signals_decoded (
    id SERIAL PRIMARY KEY,
    decision JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    trade JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    position JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);