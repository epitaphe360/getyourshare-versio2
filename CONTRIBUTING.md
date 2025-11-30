# 🤝 Guide de Contribution GetYourShare

Merci de votre intérêt pour contribuer à GetYourShare ! Ce document explique comment contribuer efficacement au projet.

## Table des Matières

- [Code de Conduite](#code-de-conduite)
- [Comment Contribuer](#comment-contribuer)
- [Standards de Code](#standards-de-code)
- [Workflow Git](#workflow-git)
- [Tests](#tests)
- [Documentation](#documentation)
- [Review Process](#review-process)

## 📜 Code de Conduite

### Notre Engagement

Nous nous engageons à faire de la participation à ce projet une expérience sans harcèlement pour tous, indépendamment de :
- L'âge, la taille corporelle, le handicap
- L'ethnicité, l'identité de genre
- Le niveau d'expérience, la nationalité
- L'apparence personnelle, la race, la religion
- L'orientation sexuelle

### Comportements Attendus

✅ **Faire :**
- Utiliser un langage accueillant et inclusif
- Respecter les points de vue différents
- Accepter les critiques constructives
- Se concentrer sur ce qui est meilleur pour la communauté
- Faire preuve d'empathie

❌ **Ne pas faire :**
- Utiliser un langage ou des images sexualisés
- Faire du trolling ou des commentaires insultants
- Harceler en public ou en privé
- Publier des informations privées sans permission
- Toute autre conduite inappropriée

### Signalement

Contactez : conduct@getyourshare.com

Toutes les plaintes seront examinées rapidement et équitablement.

## 🚀 Comment Contribuer

### Types de Contributions

1. **🐛 Bugs** : Signaler ou corriger des bugs
2. **✨ Features** : Proposer ou implémenter de nouvelles fonctionnalités
3. **📚 Documentation** : Améliorer la documentation
4. **🎨 Design** : Améliorer l'UI/UX
5. **🧪 Tests** : Ajouter ou améliorer les tests
6. **🌍 Traductions** : Ajouter de nouvelles langues

### Signaler un Bug

Avant de créer une issue :
1. Vérifier qu'elle n'existe pas déjà
2. Utiliser la dernière version
3. Reproduire le bug

**Template d'Issue :**

```markdown
**Description**
Description claire du bug.

**Reproduction**
1. Aller à '...'
2. Cliquer sur '...'
3. Observer l'erreur

**Comportement Attendu**
Ce qui devrait se passer.

**Comportement Actuel**
Ce qui se passe réellement.

**Screenshots**
Si applicable, ajoutez des captures d'écran.

**Environnement**
- OS: [ex: Windows 11]
- Navigateur: [ex: Chrome 120]
- Version: [ex: 1.0.0]

**Logs**
```
Coller les logs d'erreur ici
```
```

### Proposer une Feature

**Template de Feature Request :**

```markdown
**Problème Résolu**
Quel problème cette feature résout-elle ?

**Solution Proposée**
Description de la solution.

**Alternatives Considérées**
Avez-vous envisagé d'autres solutions ?

**Informations Additionnelles**
Tout autre contexte ou screenshots.
```

### Contribuer au Code

1. **Fork** le repository
2. **Clone** votre fork
   ```bash
   git clone https://github.com/VOTRE_USERNAME/getyourshare-versio2.git
   cd getyourshare-versio2
   ```
3. **Créer** une branche
   ```bash
   git checkout -b feature/ma-feature
   ```
4. **Développer** votre feature
5. **Committer** avec des messages clairs
6. **Push** vers votre fork
7. **Créer** une Pull Request

## 💻 Standards de Code

### Backend (Python)

#### Style Guide

Suivre **PEP 8** :
```bash
# Installer les outils
pip install black flake8 isort

# Formater le code
black .
isort .

# Vérifier
flake8 .
```

#### Conventions de Nommage

```python
# Variables et fonctions : snake_case
user_name = "John"
def get_user_by_id(user_id):
    pass

# Classes : PascalCase
class UserService:
    pass

# Constantes : UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
API_BASE_URL = "https://api.example.com"

# Privé : préfixe _
def _internal_helper():
    pass
```

#### Type Hints

Toujours utiliser les type hints :
```python
from typing import List, Optional, Dict

def get_users(
    page: int = 1,
    limit: int = 20
) -> List[Dict[str, any]]:
    """
    Récupère une liste d'utilisateurs.
    
    Args:
        page: Numéro de page (commence à 1)
        limit: Nombre d'éléments par page
        
    Returns:
        Liste de dictionnaires utilisateur
        
    Raises:
        ValueError: Si page < 1 ou limit < 1
    """
    if page < 1 or limit < 1:
        raise ValueError("page et limit doivent être >= 1")
    
    # Implementation
    return []
```

#### Docstrings

Format **Google Style** :
```python
def function_with_docstring(param1: str, param2: int) -> bool:
    """
    Brève description en une ligne.
    
    Description détaillée sur plusieurs lignes si nécessaire.
    Expliquer le comportement, les cas limites, etc.
    
    Args:
        param1: Description du premier paramètre
        param2: Description du second paramètre
        
    Returns:
        Description de ce qui est retourné
        
    Raises:
        ValueError: Quand param2 est négatif
        
    Example:
        >>> function_with_docstring("test", 5)
        True
    """
    pass
```

### Frontend (JavaScript/React)

#### Style Guide

Suivre **Airbnb Style Guide** :
```bash
# Installer ESLint
npm install --save-dev eslint

# Linter
npm run lint

# Auto-fix
npm run lint:fix
```

#### Conventions de Nommage

```javascript
// Variables et fonctions : camelCase
const userName = "John";
function getUserById(userId) {}

// Composants React : PascalCase
function UserProfile() {}

// Constantes : UPPER_SNAKE_CASE
const API_BASE_URL = "https://api.example.com";
const MAX_RETRY_COUNT = 3;

// Fichiers : 
// - Composants : PascalCase (UserProfile.jsx)
// - Utils : camelCase (apiHelper.js)
```

#### Composants React

**Functional Components avec Hooks :**
```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * UserProfile component
 * Affiche le profil d'un utilisateur
 * 
 * @param {Object} props
 * @param {string} props.userId - ID de l'utilisateur
 * @param {Function} props.onUpdate - Callback après mise à jour
 */
const UserProfile = ({ userId, onUpdate }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser();
  }, [userId]);

  const fetchUser = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/users/${userId}`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spin />;
  if (!user) return <Empty />;

  return (
    <div className="user-profile">
      <h2>{user.name}</h2>
      {/* ... */}
    </div>
  );
};

UserProfile.propTypes = {
  userId: PropTypes.string.isRequired,
  onUpdate: PropTypes.func
};

UserProfile.defaultProps = {
  onUpdate: () => {}
};

export default UserProfile;
```

#### Hooks Personnalisés

```javascript
// hooks/useApi.js
import { useState, useEffect } from 'react';
import api from '../utils/api';

/**
 * Hook personnalisé pour les appels API
 * 
 * @param {string} url - URL de l'endpoint
 * @returns {Object} { data, loading, error, refetch }
 */
export const useApi = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(url);
      setData(response.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [url]);

  return { data, loading, error, refetch: fetchData };
};
```

## 🌿 Workflow Git

### Branches

```
main          Production-ready code
  ├── develop       Development branch
      ├── feature/user-management
      ├── feature/analytics
      ├── bugfix/login-error
      └── hotfix/critical-bug
```

### Naming Convention

```
feature/nom-descriptif    Nouvelle feature
bugfix/nom-bug           Correction de bug
hotfix/bug-critique      Correction urgente
refactor/nom-refacto     Refactoring
docs/section             Documentation
test/nom-test            Ajout de tests
```

### Commit Messages

Format **Conventional Commits** :

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types :**
- `feat`: Nouvelle feature
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage (pas de changement de code)
- `refactor`: Refactoring
- `test`: Ajout/modification de tests
- `chore`: Maintenance

**Exemples :**
```bash
feat(auth): add 2FA authentication

Implement TOTP-based 2FA with QR code generation
and backup codes.

Closes #123

---

fix(api): resolve CORS issue on production

Updated CORS middleware to allow proper origins.

Fixes #456

---

docs(readme): update installation instructions

Added Docker installation steps and troubleshooting section.
```

### Pull Request

**Template de PR :**

```markdown
## Description
Brève description des changements.

## Type de Changement
- [ ] Bug fix
- [ ] Nouvelle feature
- [ ] Breaking change
- [ ] Documentation

## Changements Effectués
- Ajout de la fonctionnalité X
- Correction du bug Y
- Amélioration de Z

## Screenshots
Si applicable, ajoutez des screenshots.

## Tests
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests d'intégration ajoutés
- [ ] Testé manuellement
- [ ] Tests E2E passent

## Checklist
- [ ] Le code suit le style guide
- [ ] Documentation mise à jour
- [ ] Pas de warnings de linting
- [ ] Tests passent
- [ ] Branch à jour avec develop
```

## 🧪 Tests

### Backend Tests

```bash
# Tous les tests
pytest

# Avec coverage
pytest --cov=. --cov-report=html

# Test spécifique
pytest tests/test_auth.py

# Watch mode
pytest-watch
```

**Écrire un Test :**
```python
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_login_success():
    """Test de connexion réussie"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'token' in response.json()

def test_login_invalid_credentials():
    """Test de connexion avec mauvais identifiants"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
```

### Frontend Tests

```bash
# Tous les tests
npm test

# Avec coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Test spécifique
npm test -- UserProfile.test.js
```

**Écrire un Test :**
```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import UserProfile from './UserProfile';

describe('UserProfile', () => {
  it('renders user name', async () => {
    render(<UserProfile userId="123" />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('calls onUpdate when button clicked', () => {
    const onUpdate = jest.fn();
    render(<UserProfile userId="123" onUpdate={onUpdate} />);
    
    fireEvent.click(screen.getByText('Update'));
    
    expect(onUpdate).toHaveBeenCalledTimes(1);
  });
});
```

## 📚 Documentation

### Quoi Documenter

1. **Fonctions/Classes** : Docstrings/JSDoc
2. **API Endpoints** : Dans API_DOCUMENTATION.md
3. **Composants** : Props et usage
4. **Configuration** : Variables d'environnement
5. **Architecture** : Diagrammes et explications

### Format

**Backend (Python) :**
```python
def process_payment(
    amount: float,
    method: str,
    metadata: Optional[Dict] = None
) -> PaymentResult:
    """
    Traite un paiement.
    
    Cette fonction interagit avec le gateway de paiement configuré
    pour traiter une transaction. Elle gère la validation, le retry
    en cas d'échec temporaire, et les webhooks.
    
    Args:
        amount: Montant en euros (doit être > 0)
        method: Méthode de paiement ('card', 'paypal', 'bank')
        metadata: Données additionnelles optionnelles
        
    Returns:
        PaymentResult avec status, transaction_id et message
        
    Raises:
        ValueError: Si amount <= 0 ou method invalide
        PaymentGatewayError: Si le paiement échoue
        
    Example:
        >>> result = process_payment(99.99, 'card')
        >>> print(result.transaction_id)
        'txn_abc123'
    
    Note:
        Les paiements sont traités de manière asynchrone.
        Utilisez les webhooks pour la confirmation finale.
    """
    pass
```

**Frontend (JSDoc) :**
```javascript
/**
 * Traite un paiement via l'API
 * 
 * @param {number} amount - Montant en euros
 * @param {string} method - Méthode de paiement
 * @param {Object} [metadata] - Données additionnelles
 * @returns {Promise<PaymentResult>} Résultat du paiement
 * @throws {Error} Si le paiement échoue
 * 
 * @example
 * const result = await processPayment(99.99, 'card');
 * console.log(result.transactionId);
 */
async function processPayment(amount, method, metadata = {}) {
  // Implementation
}
```

## 🔍 Review Process

### Critères d'Acceptation

✅ **Code Quality**
- Suit les standards de code
- Bien documenté
- Tests ajoutés
- Pas de code dupliqué

✅ **Functionality**
- Fonctionne comme prévu
- Pas de régression
- Gère les cas limites

✅ **Performance**
- Pas de ralentissement
- Optimisations appropriées

✅ **Security**
- Pas de failles de sécurité
- Validation des entrées
- Échappement des sorties

### Processus

1. **Soumettre** la PR
2. **CI** s'exécute automatiquement
3. **Reviewers** assignés (minimum 1)
4. **Feedback** donné
5. **Corrections** apportées
6. **Approbation** reçue
7. **Merge** dans develop

### Donner du Feedback

**Bonnes Pratiques :**
- Être respectueux et constructif
- Expliquer le "pourquoi"
- Proposer des alternatives
- Féliciter le bon code

**Exemple de commentaire :**
```
❌ Mauvais : "Ce code est nul"

✅ Bon : "Cette fonction pourrait être optimisée en utilisant 
un dictionnaire plutôt qu'une boucle for. Cela réduirait 
la complexité de O(n²) à O(n). Qu'en penses-tu ?"
```

## 🏆 Reconnaissance

Les contributeurs seront mentionnés dans :
- README.md (section Contributors)
- CHANGELOG.md
- Release notes

Top contributeurs :
- Badge "Contributor" sur le profil
- Accès anticipé aux nouvelles features
- Invitation aux événements privés

## 📞 Questions ?

- 💬 **Discord** : https://discord.gg/getyourshare
- 📧 **Email** : dev@getyourshare.com
- 📚 **Docs** : https://docs.getyourshare.com
- 🐛 **Issues** : https://github.com/epitaphe360/getyourshare-versio2/issues

---

**Merci de contribuer à GetYourShare ! 🚀**
