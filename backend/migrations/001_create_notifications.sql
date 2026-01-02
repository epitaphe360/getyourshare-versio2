-- Migration: Create Notifications Table
-- Date: 2025-12-03
-- Description: Real-time notification system

CREATE TABLE IF NOT EXISTS notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Type & Priority
  type VARCHAR(50) NOT NULL,
  priority VARCHAR(20) DEFAULT 'medium',

  -- Content
  title VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  data JSONB DEFAULT '{}',

  -- Action
  action_url VARCHAR(500),
  action_label VARCHAR(100),

  -- Channels
  channels JSONB DEFAULT '{"in_app": true, "push": false, "email": false, "sms": false}',

  -- Status
  status VARCHAR(20) DEFAULT 'pending',
  read BOOLEAN DEFAULT FALSE,
  read_at TIMESTAMP,
  sent_at TIMESTAMP,
  delivered_at TIMESTAMP,

  -- Grouping & Expiration
  group_key VARCHAR(100),
  expires_at TIMESTAMP,
  metadata JSONB DEFAULT '{}',

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_notifications_user_read_date ON notifications(user_id, read, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_user_type ON notifications(user_id, type);
CREATE INDEX IF NOT EXISTS idx_notifications_group_key ON notifications(group_key);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_expires ON notifications(expires_at) WHERE expires_at IS NOT NULL;

-- Add push_subscription to users table if not exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS push_subscription JSONB DEFAULT NULL;

COMMENT ON TABLE notifications IS 'Real-time notification system with multi-channel support';
