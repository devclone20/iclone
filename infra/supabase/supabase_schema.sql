-- iCLONE — Supabase Schema
-- Run this in Supabase SQL Editor after creating the project
-- Tables: latest_state, trade_log, self_attendance, acp_jobs, training_log

-- ─────────────────────────────────────────────────────────
-- 1. LATEST STATE — agent runtime state (single row, upserted)
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS latest_state (
    id              SERIAL PRIMARY KEY,
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    regime          TEXT,           -- RISK-ON | RISK-OFF | TRANSITION
    macro_thesis    TEXT,
    portfolio_json  JSONB,          -- current positions snapshot
    account_equity  NUMERIC(18,6),
    drawdown_pct    NUMERIC(8,4),
    risk_mode       TEXT,           -- NORMAL | REDUCED | DEFENSIVE | SURVIVAL
    notes           TEXT
);

-- ─────────────────────────────────────────────────────────
-- 2. TRADE LOG — every trade open/close
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trade_log (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    asset           TEXT NOT NULL,          -- e.g. BTC, xyz:NVDA
    side            TEXT NOT NULL,          -- long | short
    action          TEXT NOT NULL,          -- open | close | add | reduce
    size_usdc       NUMERIC(18,6),
    entry_price     NUMERIC(18,6),
    exit_price      NUMERIC(18,6),
    pnl_usdc        NUMERIC(18,6),
    leverage        NUMERIC(6,2),
    thesis          TEXT,                   -- macro thesis for this trade
    regime          TEXT,
    seykota_score   INTEGER,                -- -7 to +7
    forum_post_id   TEXT,                   -- degen.virtuals.io post id
    status          TEXT DEFAULT 'open'     -- open | closed
);

-- ─────────────────────────────────────────────────────────
-- 3. SELF ATTENDANCE — performance log per cycle
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS self_attendance (
    id                  SERIAL PRIMARY KEY,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    cycle               TEXT,               -- e.g. "2026-06-10 00:00 UTC"
    decision_quality    INTEGER,            -- 1-10
    speed               INTEGER,            -- 1-10
    discipline          INTEGER,            -- 1-10
    learning            INTEGER,            -- 1-10
    reputation          INTEGER,            -- 1-10
    avg_score           NUMERIC(4,2),       -- computed average
    lesson_learned      TEXT,               -- key takeaway
    rule_added          TEXT                -- new rule if score < 7
);

-- ─────────────────────────────────────────────────────────
-- 4. ACP JOBS — marketplace job history
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS acp_jobs (
    id                  SERIAL PRIMARY KEY,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    job_id              TEXT UNIQUE NOT NULL,
    offering_id         TEXT NOT NULL,
    offering_name       TEXT,
    client_agent_id     TEXT,
    status              TEXT NOT NULL,      -- pending|accepted|executing|delivered|completed|disputed
    price_usdc          NUMERIC(18,6),
    requirements_json   JSONB,
    deliverable_url     TEXT,
    delivered_at        TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    usdc_earned         NUMERIC(18,6),
    erc8004_score       INTEGER             -- reputation impact
);

-- ─────────────────────────────────────────────────────────
-- 5. TRAINING LOG — training module history
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS training_log (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    module_name     TEXT NOT NULL,
    module_version  TEXT,
    session         TEXT,               -- e.g. "morning" | "evening"
    score           NUMERIC(4,2),       -- 1-10
    key_learnings   TEXT,
    github_repo     TEXT,
    papers_studied  TEXT[]              -- array of paper titles/arxiv IDs
);

-- ─────────────────────────────────────────────────────────
-- INDEXES for performance
-- ─────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_trade_log_asset     ON trade_log(asset);
CREATE INDEX IF NOT EXISTS idx_trade_log_status    ON trade_log(status);
CREATE INDEX IF NOT EXISTS idx_trade_log_created   ON trade_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_acp_jobs_status     ON acp_jobs(status);
CREATE INDEX IF NOT EXISTS idx_acp_jobs_created    ON acp_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_training_created    ON training_log(created_at DESC);

-- ─────────────────────────────────────────────────────────
-- VIEWS for quick reporting
-- ─────────────────────────────────────────────────────────

-- Total revenue from ACP jobs
CREATE OR REPLACE VIEW acp_revenue_summary AS
SELECT
    COUNT(*)                    AS total_jobs,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_jobs,
    SUM(usdc_earned)            AS total_usdc_earned,
    AVG(price_usdc)             AS avg_price,
    MAX(created_at)             AS last_job_at
FROM acp_jobs;

-- Trading performance summary
CREATE OR REPLACE VIEW trading_summary AS
SELECT
    COUNT(*)                            AS total_trades,
    COUNT(*) FILTER (WHERE pnl_usdc > 0) AS winning_trades,
    SUM(pnl_usdc)                       AS total_pnl,
    AVG(pnl_usdc)                       AS avg_pnl,
    MAX(pnl_usdc)                       AS best_trade,
    MIN(pnl_usdc)                       AS worst_trade
FROM trade_log
WHERE status = 'closed';

-- Self attendance average by week
CREATE OR REPLACE VIEW attendance_weekly AS
SELECT
    DATE_TRUNC('week', created_at) AS week,
    ROUND(AVG(avg_score), 2)       AS avg_score,
    COUNT(*)                        AS cycles_run
FROM self_attendance
GROUP BY 1
ORDER BY 1 DESC;

-- ─────────────────────────────────────────────────────────
-- Row Level Security (enable after setup)
-- ─────────────────────────────────────────────────────────
ALTER TABLE latest_state    ENABLE ROW LEVEL SECURITY;
ALTER TABLE trade_log       ENABLE ROW LEVEL SECURITY;
ALTER TABLE self_attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE acp_jobs        ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_log    ENABLE ROW LEVEL SECURITY;
