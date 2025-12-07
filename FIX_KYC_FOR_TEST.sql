-- Adaptation de la table kyc_verifications pour le scénario de test
-- Le script Python attend une structure plate spécifique

DROP TABLE IF EXISTS kyc_verifications CASCADE;

CREATE TABLE kyc_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50),
    document_type VARCHAR(50),
    document_number VARCHAR(100),
    full_name VARCHAR(255),
    date_of_birth DATE,
    address TEXT,
    phone_number VARCHAR(50),
    verification_code VARCHAR(50),
    submitted_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activer RLS
ALTER TABLE kyc_verifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all for kyc_verifications" ON kyc_verifications FOR ALL USING (true);
