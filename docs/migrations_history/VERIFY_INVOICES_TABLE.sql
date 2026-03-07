-- Vérifier si la table invoices existe vraiment
SELECT 
    table_name,
    table_schema
FROM information_schema.tables 
WHERE table_name = 'invoices';

-- Vérifier les colonnes de la table
SELECT 
    column_name, 
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'invoices'
ORDER BY ordinal_position;

-- Vérifier les politiques RLS
SELECT 
    schemaname,
    tablename,
    policyname,
    cmd,
    qual
FROM pg_policies 
WHERE tablename = 'invoices';

-- Vérifier si la table est dans le bon schéma (public)
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_name = 'invoices';
