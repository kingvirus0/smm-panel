-- SMM Panel - Payment Gateway Migration
-- Run this against your PostgreSQL database

-- Add new columns to payments table for gateway support
ALTER TABLE payments ADD COLUMN IF NOT EXISTS telegram_user_id VARCHAR(20);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS provider VARCHAR(20) DEFAULT 'manual';
ALTER TABLE payments ADD COLUMN IF NOT EXISTS reference VARCHAR(100);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS gateway_response TEXT;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP;

-- Create unique index on reference
CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_reference ON payments(reference);
CREATE INDEX IF NOT EXISTS idx_payments_telegram_user_id ON payments(telegram_user_id);

-- If payments table doesn't exist, create it:
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    telegram_user_id VARCHAR(20),
    amount DECIMAL(10,2) NOT NULL,
    method VARCHAR(20) NOT NULL,
    provider VARCHAR(20) DEFAULT 'manual',
    reference VARCHAR(100) UNIQUE NOT NULL,
    gateway_response TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    tx_reference VARCHAR(500),
    crypto_address VARCHAR(500),
    crypto_amount DECIMAL(10,8),
    proof_file_url VARCHAR(1000),
    admin_note TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    verified_at TIMESTAMP,
    processed_by VARCHAR(36)
);
