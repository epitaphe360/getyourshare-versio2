
-- Add status column to products if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'status') THEN 
        ALTER TABLE products ADD COLUMN status TEXT DEFAULT 'active'; 
    END IF; 
END $$;

-- Add status column to reviews if it doesn't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'reviews' AND column_name = 'status') THEN 
        ALTER TABLE reviews ADD COLUMN status TEXT DEFAULT 'pending'; 
    END IF; 
END $$;
