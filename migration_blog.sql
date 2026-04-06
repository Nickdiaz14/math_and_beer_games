-- SQLBook: Code
-- Active: 1774031322036@@aws-0-us-west-1.pooler.supabase.com@5432@postgres
-- ============================================================
-- NUEVAS TABLAS PARA FUNCIONALIDAD BLOG / COMUNIDAD
-- Math & Beer Games
-- ============================================================

-- 1. COMENTARIOS en charlas pasadas (solo usuarios con Nickname)
CREATE TABLE IF NOT EXISTS comments (
    id          SERIAL PRIMARY KEY,
    event_id    INTEGER NOT NULL,          -- ID del evento al que pertenece (events.id)
    userid      TEXT NOT NULL,             -- UUID del usuario (viene de localStorage igual que leaderboard)
    content     TEXT NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para acelerar consultas por evento
CREATE INDEX IF NOT EXISTS idx_comments_event_id ON comments(event_id);

-- 2. REACCIONES (brindis 🍻) por charla — una por usuario por evento
CREATE TABLE IF NOT EXISTS reactions (
    id          SERIAL PRIMARY KEY,
    event_id    INTEGER NOT NULL,
    userid      TEXT NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (event_id, userid)              -- Evita duplicados: 1 brindis por usuario por charla
);

-- 3. SUSCRIPTORES a notificaciones de próximos eventos
CREATE TABLE IF NOT EXISTS subscribers (
    id          SERIAL PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,      -- Correo único para la lista
    name        TEXT,                      -- Nombre opcional
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
