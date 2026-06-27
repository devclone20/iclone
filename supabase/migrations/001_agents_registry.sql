-- iCLONE Agent Registry
-- Tracks all agents: providers, dedicated clients, and future agents

create table if not exists public.agents (
    -- Identity
    id                  uuid primary key default gen_random_uuid(),
    agent_id            text unique not null,          -- Virtuals UUID (019eae06-...)
    name                text not null,                  -- Display name
    role                text not null,                  -- PROVIDER | CLIENT | HYBRID
    purpose             text,                           -- human description of what this agent does

    -- Wallets
    evm_wallet          text unique,                    -- 0x... Base mainnet
    sol_wallet          text,                           -- Solana wallet (if any)

    -- Virtuals identifiers
    virtual_agent_id    integer,                        -- virtualAgentId (85280 for CLONE)
    erc8004_agent_id    integer,                        -- ERC-8004 identity registry id
    acpv2_agent_id      integer,                        -- ACP v2 agent id
    builder_code        text,                           -- bc_4xeitn8j
    entity_id           integer,                        -- Virtuals entity id (1440 for CLONE)

    -- Token (if tokenized)
    token_symbol        text,                           -- ICLONE
    token_address       text,                           -- 0x43EC40...
    chain_id            integer default 8453,

    -- Status
    is_active           boolean default true,
    is_tokenized        boolean default false,
    signer_policy       text default 'unrestricted',   -- restricted | unrestricted | deny-all

    -- Operational config
    daily_budget_usdc   numeric(10,4),                  -- for CLIENT agents
    max_job_price_usdc  numeric(10,4),                  -- for CLIENT agents
    jobs_per_hour       integer,                        -- for CLIENT agents
    target_provider     text,                           -- for CLIENT agents: wallet to hire

    -- Stats (updated daily)
    total_jobs_created  integer default 0,
    total_jobs_completed integer default 0,
    total_spent_usdc    numeric(12,4) default 0,
    total_earned_usdc   numeric(12,4) default 0,

    -- Metadata
    notes               text,
    created_at          timestamptz default now(),
    updated_at          timestamptz default now()
);

-- Auto-update updated_at
create or replace function update_agents_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

create trigger agents_updated_at
    before update on public.agents
    for each row execute function update_agents_updated_at();

-- Seed: CLONE (existing provider)
insert into public.agents (
    agent_id, name, role, purpose,
    evm_wallet, sol_wallet,
    virtual_agent_id, erc8004_agent_id, builder_code, entity_id,
    token_symbol, token_address, chain_id,
    is_active, is_tokenized, signer_policy,
    notes
) values (
    '019eae06-96cd-77d0-8f8b-a6abb71f0cd7',
    'CLONE', 'PROVIDER',
    'Main iCLONE provider agent. Sells 32 offerings: research, code, crypto, content, DeFi.',
    '0x44cc25d55a4291b92f52062ba023ca1f14206664',
    '8qegkxDvmh7JG8nEo7vJp2forM8f67DjHThDkyzsbQQp',
    85280, 55101, 'bc_4xeitn8j', 1440,
    'ICLONE', '0x43EC40d6a4Fad9e4E804dd3C0e1527ef12221Cfa', 8453,
    true, true, 'unrestricted',
    'First agent. Server running via acp-cli CLI-backed architecture. Bootstrapper active.'
) on conflict (agent_id) do nothing;

-- Index for fast lookups
create index if not exists idx_agents_role on public.agents(role);
create index if not exists idx_agents_evm_wallet on public.agents(evm_wallet);
create index if not exists idx_agents_is_active on public.agents(is_active);
