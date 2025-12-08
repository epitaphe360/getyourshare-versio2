-- ============================================
-- Migration 004: Fix Support Tickets Columns
-- Date: 2025-12-08
-- Description: Add missing columns to support_tickets table
-- ============================================

-- Add missing columns to support_tickets if they don't exist
DO $$
BEGIN
    -- Add assigned_to column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'support_tickets' AND column_name = 'assigned_to'
    ) THEN
        ALTER TABLE support_tickets ADD COLUMN assigned_to UUID REFERENCES users(id);
        RAISE NOTICE 'Added column assigned_to to support_tickets';
    END IF;

    -- Add sla_due_at column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'support_tickets' AND column_name = 'sla_due_at'
    ) THEN
        ALTER TABLE support_tickets ADD COLUMN sla_due_at TIMESTAMP;
        RAISE NOTICE 'Added column sla_due_at to support_tickets';
    END IF;

    -- Add resolved_at column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'support_tickets' AND column_name = 'resolved_at'
    ) THEN
        ALTER TABLE support_tickets ADD COLUMN resolved_at TIMESTAMP;
        RAISE NOTICE 'Added column resolved_at to support_tickets';
    END IF;

    -- Add closed_at column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'support_tickets' AND column_name = 'closed_at'
    ) THEN
        ALTER TABLE support_tickets ADD COLUMN closed_at TIMESTAMP;
        RAISE NOTICE 'Added column closed_at to support_tickets';
    END IF;

    -- Add metadata column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'support_tickets' AND column_name = 'metadata'
    ) THEN
        ALTER TABLE support_tickets ADD COLUMN metadata JSONB DEFAULT '{}';
        RAISE NOTICE 'Added column metadata to support_tickets';
    END IF;
END $$;

-- Create indexes if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_support_tickets_assigned'
    ) THEN
        CREATE INDEX idx_support_tickets_assigned ON support_tickets(assigned_to);
        RAISE NOTICE 'Created index idx_support_tickets_assigned';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_support_tickets_status'
    ) THEN
        CREATE INDEX idx_support_tickets_status ON support_tickets(status);
        RAISE NOTICE 'Created index idx_support_tickets_status';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_support_tickets_user'
    ) THEN
        CREATE INDEX idx_support_tickets_user ON support_tickets(user_id);
        RAISE NOTICE 'Created index idx_support_tickets_user';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_support_tickets_created'
    ) THEN
        CREATE INDEX idx_support_tickets_created ON support_tickets(created_at DESC);
        RAISE NOTICE 'Created index idx_support_tickets_created';
    END IF;
END $$;

-- ============================================
-- END OF MIGRATION
-- ============================================
