-- labubot.db: lo que se recuerda entre corridas, compartido por la api (webhook) y el worker.
-- Fechas ISO 8601 en TEXT, UTC. Los PRAGMA van en connect().

CREATE TABLE IF NOT EXISTS users (
  chat_id     INTEGER PRIMARY KEY,             -- chat privado = id del usuario de Telegram
  username    TEXT,                            -- @usuario, puede faltar
  first_name  TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'pending', -- UserStatus: pending | active | paused | rejected | blocked
  profile     TEXT NOT NULL DEFAULT '',        -- el CV; '' = todavía no lo cargó
  state       TEXT NOT NULL DEFAULT '',        -- ChatState: qué espera el bot del próximo mensaje ('' = nada)
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_terms (
  chat_id INTEGER NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
  term    TEXT NOT NULL,                       -- en minúsculas
  PRIMARY KEY (chat_id, term)
);

CREATE TABLE IF NOT EXISTS user_blocked_words (
  chat_id INTEGER NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
  word    TEXT NOT NULL,                       -- en minúsculas; se busca como substring del título en minúsculas
  PRIMARY KEY (chat_id, word)
);

CREATE TABLE IF NOT EXISTS offers (            -- caché compartida de descripciones: una bajada por url
  url         TEXT PRIMARY KEY NOT NULL,       -- sin query
  portal      TEXT NOT NULL,                   -- nombre de la clase: LinkedIn, Bumeran...
  title       TEXT NOT NULL,
  description TEXT NOT NULL                    -- '' si el portal no la dio (no se vuelve a pedir)
);

CREATE TABLE IF NOT EXISTS deliveries (        -- qué ya se evaluó para cada usuario
  chat_id       INTEGER NOT NULL REFERENCES users(chat_id) ON DELETE CASCADE,
  url           TEXT NOT NULL,                 -- sin FK a offers: las importadas de vistas.txt no tienen fila en offers
  term          TEXT,                          -- palabra clave que la trajo; NULL = "Otros portales" o importada de vistas.txt
  light         TEXT,                          -- TrafficLight: green | yellow | red; NULL = importada de vistas.txt
  classified_at TEXT NOT NULL,
  sent_at       TEXT,                          -- NULL si es roja, importada, o si el envío falló (se reintenta)
  PRIMARY KEY (chat_id, url)
);
