-- labubot.db, compartida por la api (webhook) y el worker. Los PRAGMA van en connect().

CREATE TABLE IF NOT EXISTS users (
  chat_id     INTEGER PRIMARY KEY,
  username    TEXT,
  first_name  TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'pending',
  profile     TEXT NOT NULL DEFAULT '',
  state       TEXT NOT NULL DEFAULT '',
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_terms (
  chat_id INTEGER NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
  term    TEXT NOT NULL,
  PRIMARY KEY (chat_id, term)
);

CREATE TABLE IF NOT EXISTS user_blocked_words (
  chat_id INTEGER NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
  word    TEXT NOT NULL,
  PRIMARY KEY (chat_id, word)
);

CREATE TABLE IF NOT EXISTS offers (
  url         TEXT PRIMARY KEY NOT NULL,
  portal      TEXT NOT NULL,
  title       TEXT NOT NULL,
  description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deliveries (
  chat_id       INTEGER NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
  url           TEXT NOT NULL, -- sin FK a offers: las importadas de vistas.txt no tienen fila ahí
  term          TEXT,
  light         TEXT,
  classified_at TEXT NOT NULL,
  sent_at       TEXT,
  PRIMARY KEY (chat_id, url)
);

CREATE TABLE IF NOT EXISTS search_requests (
  chat_id      INTEGER PRIMARY KEY REFERENCES users(chat_id) ON DELETE CASCADE,
  requested_at TEXT NOT NULL
);
