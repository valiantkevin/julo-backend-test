DROP TABLE IF EXISTS authorization;

CREATE TABLE authorization 
(
    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_xid TEXT NOT NULL,
    token TEXT NOT NULL
);

DROP TABLE IF EXISTS wallets;

CREATE TABLE wallets
(
    wallet_key INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id TEXT NOT NULL,
    customer_key INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'disabled',
    last_status_change TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    balance INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS deposits;

CREATE TABLE deposits
(
    deposit_id TEXT PRIMARY KEY,
    deposited_by INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    deposited_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount INTEGER NOT NULL DEFAULT 0,
    reference_id TEXT NOT NULL UNIQUE
);

DROP TABLE IF EXISTS withdrawals;

CREATE TABLE withdrawals
(
    withdrawal_id TEXT PRIMARY KEY,
    withdrawed_by INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    withdrawed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount INTEGER NOT NULL DEFAULT 0,
    reference_id TEXT NOT NULL UNIQUE
);