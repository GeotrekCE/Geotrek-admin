-- Used to ensure extension is enabled even in test database (migrations disabled)
-- Otherwise UUIDs on objects can not be generated on insert (including path splits)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";