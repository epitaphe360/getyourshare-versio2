-- Add missing columns for affiliate stats
ALTER TABLE users ADD COLUMN IF NOT EXISTS clicks INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS conversions INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS traffic_source TEXT;

-- Verify columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('clicks', 'conversions', 'traffic_source');
