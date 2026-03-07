-- ========================================
-- AJOUTER POLITIQUES RLS POUR LES ADMINS
-- ========================================

-- Politique pour que les admins puissent voir toutes les conversations
CREATE POLICY "Admins can view all conversations"
ON conversations
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE users.id = auth.uid() 
        AND users.role = 'admin'
    )
);

-- Politique pour que les admins puissent voir tous les messages
CREATE POLICY "Admins can view all messages"
ON messages
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE users.id = auth.uid() 
        AND users.role = 'admin'
    )
);

-- Politique pour que les admins puissent envoyer des messages
CREATE POLICY "Admins can send messages"
ON messages
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM users 
        WHERE users.id = auth.uid() 
        AND users.role = 'admin'
    )
);

-- Vérifier que les politiques ont été créées
SELECT 
    tablename,
    policyname,
    cmd,
    roles
FROM pg_policies 
WHERE tablename IN ('conversations', 'messages')
ORDER BY tablename, policyname;
