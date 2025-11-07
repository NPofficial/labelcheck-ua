-- =====================================================
-- SUPABASE MIGRATION: check_sessions table
-- =====================================================
-- Таблиця для зберігання сесій перевірки етикеток
-- Автор: LabelCheck UA Team
-- Дата: 2025-11-06
-- Версія: 1.0

-- =====================================================
-- ТАБЛИЦЯ: check_sessions
-- =====================================================
-- Зберігає дані про сесії перевірки етикеток (2-кроковий процес)

CREATE TABLE IF NOT EXISTS check_sessions (
    id SERIAL PRIMARY KEY,
    check_id UUID UNIQUE NOT NULL,
    label_data JSONB NOT NULL,
    report JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'extracted',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Індекси для швидкого пошуку
CREATE INDEX IF NOT EXISTS idx_check_id ON check_sessions(check_id);
CREATE INDEX IF NOT EXISTS idx_created_at ON check_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_status ON check_sessions(status);

-- Коментарі для документації
COMMENT ON TABLE check_sessions IS 'Сесії перевірки етикеток дієтичних добавок';
COMMENT ON COLUMN check_sessions.check_id IS 'Унікальний UUID сесії перевірки';
COMMENT ON COLUMN check_sessions.label_data IS 'Витягнуті дані з етикетки (OCR результат)';
COMMENT ON COLUMN check_sessions.report IS 'Повний звіт про перевірку (після Step 2)';
COMMENT ON COLUMN check_sessions.status IS 'Статус: extracted, completed, failed';

