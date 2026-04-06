-- =============================================
-- migration_features.sql
-- Nuevas tablas para features de comunidad
-- Math & Beer Games
-- =============================================

-- Feature 2: RSVP / Check-in para próximas charlas
CREATE TABLE IF NOT EXISTS rsvp (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id),
    userid VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, userid)
);

-- Feature 5: Preguntas previas al ponente (Q&A)
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id),
    userid VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS question_votes (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    userid VARCHAR(100) NOT NULL,
    UNIQUE(question_id, userid)
);
