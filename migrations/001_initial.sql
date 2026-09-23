-- project-tracker: initial schema
-- Run: psql $DATABASE_URL -f migrations/001_initial.sql

CREATE TABLE IF NOT EXISTS projects (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS team_members (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    role            VARCHAR(100) DEFAULT '',
    email           VARCHAR(200) DEFAULT '',
    capacity_hours  NUMERIC(5,1) DEFAULT 40.0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS milestones (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    status      VARCHAR(20) DEFAULT 'open'
                    CHECK (status IN ('open', 'closed')),
    target_date DATE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(300) NOT NULL,
    description     TEXT DEFAULT '',
    status          VARCHAR(20) DEFAULT 'backlog'
                        CHECK (status IN ('backlog','todo','in_progress',
                                          'in_review','done','blocked')),
    priority        VARCHAR(20) DEFAULT 'medium'
                        CHECK (priority IN ('low','medium','high','critical')),
    assignee_id     INTEGER REFERENCES team_members(id),
    milestone_id    INTEGER REFERENCES milestones(id),
    estimated_hours NUMERIC(6,1) DEFAULT 0,
    actual_hours    NUMERIC(6,1) DEFAULT 0,
    due_date        DATE,
    tags            TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_milestone ON tasks(milestone_id);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
