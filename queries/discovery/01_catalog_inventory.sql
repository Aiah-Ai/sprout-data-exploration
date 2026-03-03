-- Session 1: Schema Discovery — Catalog & Table Inventory
-- Executed: 2026-03-02

-- Step 1: List all schemas in prod catalog
SHOW SCHEMAS IN prod;
-- Result: 21 schemas

-- Step 2: List tables in each schema
SHOW TABLES IN prod.curated_hr;           -- 1 table
SHOW TABLES IN prod.master_hr;            -- 1 table
SHOW TABLES IN prod.raw_hr;               -- 25 tables
SHOW TABLES IN prod.staged_hr;            -- 2 tables
SHOW TABLES IN prod.curated_insight;      -- 6 tables
SHOW TABLES IN prod.master_insight;       -- 6 tables
SHOW TABLES IN prod.curated_requests;     -- 12 tables
SHOW TABLES IN prod.curated_pyo;          -- 2 tables
SHOW TABLES IN prod.curated_billing;      -- 3 tables
SHOW TABLES IN prod.master_fintech;       -- 6 tables
SHOW TABLES IN prod.raw_payroll;          -- 12 tables
SHOW TABLES IN prod.staged_payroll;       -- 1 table
SHOW TABLES IN prod.raw_readycash;        -- 14 tables
SHOW TABLES IN prod.raw_readywage;        -- 10 tables
SHOW TABLES IN prod.curated_readycash;    -- 6 tables
SHOW TABLES IN prod.curated_readywage;    -- 3 tables
SHOW TABLES IN prod.staged_readycash;     -- 2 tables
SHOW TABLES IN prod.staged_readywage;     -- 2 tables
SHOW TABLES IN prod.ai_sidekick_central;  -- 5 tables
SHOW TABLES IN prod.ai_payroll_outsourcing_platform; -- 0 tables
