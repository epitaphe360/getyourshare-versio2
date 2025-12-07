-- Migration: Ajouter user_id à payouts
-- Date: 2024-12-06

ALTER TABLE payouts 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;

COMMENT ON COLUMN payouts.user_id IS 'ID de l''utilisateur demandant le retrait';
