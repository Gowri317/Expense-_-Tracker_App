-- ============================================================================
-- Expense Tracker — Supabase PostgreSQL Schema
-- Run this entire file in the Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================================

-- ── 1. Categories Table ─────────────────────────────────────────────────────
-- user_id = NULL means it's a default (global) category.
-- user_id = <uuid> means it's a user-created custom category.

CREATE TABLE IF NOT EXISTS categories (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL CHECK (char_length(name) <= 100),
    user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- ── 2. Expenses Table ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS expenses (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    amount      DOUBLE PRECISION NOT NULL CHECK (amount > 0),
    category_id BIGINT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    date        DATE NOT NULL DEFAULT CURRENT_DATE,
    note        TEXT CHECK (note IS NULL OR char_length(note) <= 500),
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- ── 3. Incomes Table ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS incomes (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    amount      DOUBLE PRECISION NOT NULL CHECK (amount > 0),
    source      TEXT NOT NULL CHECK (char_length(source) <= 200),
    date        DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- ── 4. Budgets Table ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS budgets (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category_id BIGINT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    amount      DOUBLE PRECISION NOT NULL CHECK (amount > 0),
    month       TEXT NOT NULL CHECK (month ~ '^\d{4}-\d{2}$'),
    created_at  TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT uq_user_category_month UNIQUE (user_id, category_id, month)
);

-- ── 5. Indexes for Performance ──────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses (user_id, date);
CREATE INDEX IF NOT EXISTS idx_expenses_category  ON expenses (category_id);
CREATE INDEX IF NOT EXISTS idx_incomes_user_date  ON incomes (user_id, date);
CREATE INDEX IF NOT EXISTS idx_budgets_user_month ON budgets (user_id, month);
CREATE INDEX IF NOT EXISTS idx_categories_user    ON categories (user_id);

-- ── 6. Enable Row Level Security ────────────────────────────────────────────

ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses   ENABLE ROW LEVEL SECURITY;
ALTER TABLE incomes    ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets    ENABLE ROW LEVEL SECURITY;

-- ── 7. RLS Policies — Categories ────────────────────────────────────────────
-- Everyone (authenticated) can read default categories (user_id IS NULL)
-- plus their own custom categories.

CREATE POLICY "categories_select"
    ON categories FOR SELECT
    TO authenticated
    USING (user_id IS NULL OR user_id = auth.uid());

CREATE POLICY "categories_insert"
    ON categories FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "categories_update"
    ON categories FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "categories_delete"
    ON categories FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());

-- ── 8. RLS Policies — Expenses ──────────────────────────────────────────────

CREATE POLICY "expenses_select"
    ON expenses FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "expenses_insert"
    ON expenses FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "expenses_update"
    ON expenses FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "expenses_delete"
    ON expenses FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());

-- ── 9. RLS Policies — Incomes ───────────────────────────────────────────────

CREATE POLICY "incomes_select"
    ON incomes FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "incomes_insert"
    ON incomes FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "incomes_update"
    ON incomes FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "incomes_delete"
    ON incomes FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());

-- ── 10. RLS Policies — Budgets ──────────────────────────────────────────────

CREATE POLICY "budgets_select"
    ON budgets FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "budgets_insert"
    ON budgets FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "budgets_update"
    ON budgets FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "budgets_delete"
    ON budgets FOR DELETE
    TO authenticated
    USING (user_id = auth.uid());

-- ── 11. Seed Default Categories ─────────────────────────────────────────────

INSERT INTO categories (name, user_id) VALUES
    ('Food',          NULL),
    ('Transport',     NULL),
    ('Bills',         NULL),
    ('Entertainment', NULL),
    ('Shopping',      NULL),
    ('Health',        NULL),
    ('Education',     NULL),
    ('Other',         NULL)
ON CONFLICT DO NOTHING;
