-- iCLONE Dedicated CLIENT Agents
-- Created 2026-06-12 via acp-cli (free, no VIRTUAL tokens)
-- Fund each wallet with $50 USDC on Base mainnet before activating

INSERT INTO public.agents (
    agent_id, name, role, purpose,
    evm_wallet, sol_wallet, is_active, is_tokenized,
    signer_policy, daily_budget_usdc,
    max_job_price_usdc, jobs_per_hour,
    target_provider, notes
) VALUES
(
    '019ebb92-7415-7baa-93e9-ee19a7742877',
    'SuperSayatin', 'CLIENT',
    'Dedicated CLIENT agent. Hires iCLONE for research and crypto analysis.',
    '0x18f3aeadbad9c4b626c114ab14b89e586e4f6df3',
    '8U8j5TUZymo2ntDcbaHmKH7F21s2ZsjxLWemAa4s3D9b',  -- Solana (if needed)
    false, false,
    'unrestricted', 10.0, 0.10, 10,
    '0x44cc25d55a4291b92f52062ba023ca1f14206664',
    'Pending funding: needs $50 USDC on Base mainnet.'
),
(
    '019ebb92-93e8-7b4e-b2e8-39c3419843c9',
    'DoctorWHO', 'CLIENT',
    'Dedicated CLIENT agent. Hires iCLONE for content creation and writing.',
    '0x875242eb5c91270ca80ed7753a87d6e22e4f5acf',
    '9hifim1aAckQnbDb3P4LmzKkyMx5w5mBLjQmer2Ch5D5',
    false, false,
    'unrestricted', 10.0, 0.10, 10,
    '0x44cc25d55a4291b92f52062ba023ca1f14206664',
    'Pending funding: needs $50 USDC on Base mainnet.'
),
(
    '019ebb92-b4be-7660-82d3-4b1647843e6a',
    'MATRIX', 'CLIENT',
    'Dedicated CLIENT agent. Hires iCLONE for code and technical analysis.',
    '0x07924dea2c8212969d5dc5655785aa5063adb2bc',
    '8U8j5TUZymo2ntDcbaHmKH7F21s2ZsjxLWemAa4s3D9b',
    false, false,
    'unrestricted', 10.0, 0.10, 10,
    '0x44cc25d55a4291b92f52062ba023ca1f14206664',
    'Pending funding: needs $50 USDC on Base mainnet.'
)
ON CONFLICT (agent_id) DO UPDATE SET
    name = EXCLUDED.name,
    evm_wallet = EXCLUDED.evm_wallet,
    notes = EXCLUDED.notes;
