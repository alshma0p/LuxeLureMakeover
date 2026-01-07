CREATE TABLE IF NOT EXISTS users (
  id VARCHAR PRIMARY KEY,
  created_at TIMESTAMP,
  referral_code VARCHAR UNIQUE,
  invited_by VARCHAR,
  wallet_balance INTEGER DEFAULT 0,
  referral_completed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS scans (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR REFERENCES users(id),
  created_at TIMESTAMP,
  predicted_label VARCHAR,
  confidence FLOAT,
  attributes VARCHAR,
  unlocked BOOLEAN DEFAULT FALSE,
  unlocked_via VARCHAR,
  model_name VARCHAR,
  model_version_hash VARCHAR
);

CREATE TABLE IF NOT EXISTS wallet_ledger (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR REFERENCES users(id),
  created_at TIMESTAMP,
  amount INTEGER,
  type VARCHAR,
  description VARCHAR
);

CREATE TABLE IF NOT EXISTS minimal_logs (
  id VARCHAR PRIMARY KEY,
  request_id VARCHAR,
  route VARCHAR,
  method VARCHAR,
  status_code INTEGER,
  latency_ms INTEGER,
  user_id VARCHAR,
  error_code VARCHAR,
  created_at TIMESTAMP
);
