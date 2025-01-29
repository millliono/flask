-- Initialize the database.
-- Drop any existing data and create empty tables.
-- Create admin 

DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  credits INTEGER NOT NULL DEFAULT 0,
  is_admin BOOLEAN DEFAULT FALSE
);

-- password: loxagos
INSERT INTO user (username, password, is_admin) 
VALUES ('admin', 'scrypt:32768:8:1$rZAKNG3sfeyIKlcB$f46d1f19417c5dda9d5c874893891ced9e1b5a3634806fde7b66ca0ea5ad4eb97e5c360210d63f6d2a1319391e8187c1e93fc90db40edf7c22450623229a1d33', TRUE);