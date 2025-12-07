-- Migration to add service_id to affiliation tables
-- Date: 2025-12-05

-- 1. Update affiliation_requests
ALTER TABLE affiliation_requests 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

ALTER TABLE affiliation_requests 
ALTER COLUMN product_id DROP NOT NULL;

ALTER TABLE affiliation_requests 
DROP CONSTRAINT IF EXISTS affiliation_requests_influencer_id_product_id_key;

ALTER TABLE affiliation_requests 
ADD CONSTRAINT affiliation_requests_target_check 
CHECK (
    (product_id IS NOT NULL AND service_id IS NULL) OR 
    (product_id IS NULL AND service_id IS NOT NULL)
);

ALTER TABLE affiliation_requests 
ADD CONSTRAINT affiliation_requests_unique_target 
UNIQUE (influencer_id, product_id, service_id);

-- 2. Update affiliate_links
ALTER TABLE affiliate_links 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

ALTER TABLE affiliate_links 
ALTER COLUMN product_id DROP NOT NULL;

ALTER TABLE affiliate_links 
ADD CONSTRAINT affiliate_links_target_check 
CHECK (
    (product_id IS NOT NULL AND service_id IS NULL) OR 
    (product_id IS NULL AND service_id IS NOT NULL)
);

-- 3. Update trackable_links (if used)
ALTER TABLE trackable_links 
ADD COLUMN IF NOT EXISTS service_id UUID REFERENCES services(id) ON DELETE CASCADE;

ALTER TABLE trackable_links 
ALTER COLUMN product_id DROP NOT NULL;

-- 4. Update trigger function for auto-approval
CREATE OR REPLACE FUNCTION create_tracking_link_on_approval()
RETURNS TRIGGER AS $$
BEGIN
    -- Si la demande vient d'être approuvée
    IF NEW.status = 'approved' AND OLD.status = 'pending' THEN
        -- Créer un lien de tracking dans trackable_links (et affiliate_links pour synchro)
        -- Note: On insère dans affiliate_links car c'est ce que l'API utilise
        INSERT INTO affiliate_links (
            influencer_id,
            product_id,
            service_id,
            unique_code,
            is_active,
            created_at
        )
        VALUES (
            NEW.influencer_id,
            NEW.product_id,
            NEW.service_id,
            substring(md5(random()::text || NEW.influencer_id::text || COALESCE(NEW.product_id::text, NEW.service_id::text)) from 1 for 8),
            true,
            NOW()
        );
        
        -- Enregistrer dans l'historique
        INSERT INTO affiliation_request_history (
            request_id,
            old_status,
            new_status,
            changed_by,
            comment
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            NEW.reviewed_by,
            'Demande approuvée - Lien de tracking créé automatiquement'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
