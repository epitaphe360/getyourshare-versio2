
-- -- Add captured_at column to social_media_stats
ALTER TABLE public.social_media_stats 
ADD COLUMN IF NOT EXISTS captured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
