-- Create notification_settings table
CREATE TABLE IF NOT EXISTS notification_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    settings JSONB DEFAULT '{"email": true, "push": true, "sms": false, "sales": true, "payments": true, "messages": true, "system": true}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_notification_settings UNIQUE (user_id)
);

-- Enable RLS
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own notification settings"
    ON notification_settings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own notification settings"
    ON notification_settings FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own notification settings"
    ON notification_settings FOR INSERT
    WITH CHECK (auth.uid() = user_id);
