# 🚀 ACTION REQUISE : Ajout des Plans d'Abonnement Manquants

Pour que la section abonnement fonctionne parfaitement pour **tous les rôles** (Commerciaux, Influenceurs, Marchands), il est nécessaire d'ajouter les plans spécifiques qui manquent actuellement dans la base de données.

## 🛠️ Procédure

1.  Connectez-vous à votre tableau de bord Supabase : [https://supabase.com/dashboard](https://supabase.com/dashboard)
2.  Sélectionnez votre projet (`iamezkmapbhlhhvvsits`).
3.  Allez dans la section **SQL Editor** (icône de terminal `>_` dans la barre latérale gauche).
4.  Cliquez sur **New Query**.
5.  Copiez l'intégralité du contenu du fichier `ADD_MISSING_PLANS.sql` (situé à la racine du projet).
6.  Collez le code dans l'éditeur SQL de Supabase.
7.  Cliquez sur le bouton **Run**.

## 📋 Ce que cela ajoute

*   **Plan Marketplace (99 MAD)** : Spécifique pour les **Commerciaux** et **Influenceurs**.
*   **Plan Small (199 MAD)** : Pour les petits **Marchands**.
*   **Plan Medium (499 MAD)** : Pour les **Marchands** en croissance.
*   **Plan Large (799 MAD)** : Pour les gros **Marchands**.

Une fois ajouté, chaque utilisateur verra les plans adaptés à son profil.
