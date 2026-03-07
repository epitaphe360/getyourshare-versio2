-- Ajouter la colonne last_login à la table users si elle n'existe pas
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ DEFAULT NOW();

-- Créer un index pour améliorer les performances des requêtes sur last_login
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);

-- Mettre à jour last_login pour tous les utilisateurs existants
UPDATE users SET last_login = NOW() WHERE last_login IS NULL;

-- Vérifier que la colonne a été ajoutée
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'last_login';
