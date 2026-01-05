-- Migration to add service_id and ensure product_id exists in social_media_publications
-- Date: 2025-12-05

-- 1. Ensure product_id exists (it might be missing based on error)
ALTER TABLE social_media_publications 
ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES products(id) ON DELETE SET NULL;

-- 2. Add service_id
ALTER TABLE social_media_publications 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

-- [AUTOMATION STEP 2 & 3]: This column allows linking a publication directly to a Service, 
-- enabling the "Influencer Request" scenario for services, distinct from products.

-- 3. Make product_id nullable (it should be already if we just added it, but if it existed as NOT NULL, this fixes it)
ALTER TABLE social_media_publications 
ALTER COLUMN product_id DROP NOT NULL;

-- 4. Same for tracking_links
ALTER TABLE tracking_links 
ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES products(id) ON DELETE SET NULL;

-- [AUTOMATION STEP 4]: Stores the reference for QR Code generation specific to a Product.

ALTER TABLE tracking_links 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

-- [AUTOMATION STEP 4]: Stores the reference for QR Code generation specific to a Service.

ALTER TABLE tracking_links 
ALTER COLUMN product_id DROP NOT NULL;

-- 5. Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_publications_service_id ON social_media_publications(service_id);
CREATE INDEX IF NOT EXISTS idx_tracking_links_service_id ON tracking_links(service_id);
