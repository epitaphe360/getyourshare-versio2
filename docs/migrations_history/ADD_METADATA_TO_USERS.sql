-- ============================================
-- MIGRATION: ADD METADATA TO USERS
-- ============================================

-- Add metadata column to users table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'users'
        AND column_name = 'metadata'
    ) THEN
        ALTER TABLE users ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
        RAISE NOTICE 'Column metadata added to users table';
    ELSE
        RAISE NOTICE 'Column metadata already exists in users table';
    END IF;
END $$;

-- Update test users with metadata for AI features
UPDATE users
SET metadata = jsonb_build_object('niche', 'Fashion')
WHERE id = '33333333-3333-3333-3333-333333333333'; -- Sarah Lifestyle

UPDATE users
SET metadata = jsonb_build_object('niche', 'Tech')
WHERE id = '33333333-3333-3333-3333-333333333334'; -- Ahmed Tech

UPDATE users
SET metadata = jsonb_build_object('niche', 'Beauty')
WHERE id = '33333333-3333-3333-3333-333333333335'; -- Fatima Beauty

-- Verify
SELECT id, email, metadata FROM users WHERE id IN (
    '33333333-3333-3333-3333-333333333333',
    '33333333-3333-3333-3333-333333333334',
    '33333333-3333-3333-3333-333333333335'
);
