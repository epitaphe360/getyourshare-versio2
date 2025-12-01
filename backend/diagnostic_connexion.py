"""
Script de diagnostic pour vérifier les utilisateurs et tester la connexion
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import bcrypt

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def list_all_users():
    """Lister tous les utilisateurs dans la base"""
    print("\n" + "="*60)
    print("📋 LISTE DES UTILISATEURS DANS LA BASE DE DONNÉES")
    print("="*60 + "\n")
    
    try:
        response = supabase.table('users').select('*').execute()
        users = response.data
        
        if not users:
            print("❌ Aucun utilisateur trouvé dans la base de données!")
            print("\n💡 Suggestion: Créer des utilisateurs de test")
            return []
        
        print(f"✅ {len(users)} utilisateur(s) trouvé(s):\n")
        
        for i, user in enumerate(users, 1):
            print(f"{i}. ID: {user.get('id')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Rôle: {user.get('role', 'N/A')}")
            print(f"   Actif: {'✅ Oui' if user.get('is_active', True) else '❌ Non'}")
            print(f"   Mot de passe hash: {'✅ Présent' if user.get('password_hash') else '❌ MANQUANT'}")
            print(f"   Date création: {user.get('created_at', 'N/A')}")
            print(f"   Dernière connexion: {user.get('last_login', 'Jamais')}")
            print()
        
        return users
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des utilisateurs: {e}")
        return []

def test_user_login(email, password):
    """Tester la connexion d'un utilisateur"""
    print("\n" + "="*60)
    print(f"🔐 TEST DE CONNEXION POUR: {email}")
    print("="*60 + "\n")
    
    try:
        # Récupérer l'utilisateur
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if not response.data:
            print(f"❌ Utilisateur non trouvé: {email}")
            return False
        
        user = response.data[0]
        print(f"✅ Utilisateur trouvé:")
        print(f"   ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Rôle: {user.get('role')}")
        print(f"   Actif: {'✅ Oui' if user.get('is_active', True) else '❌ Non'}")
        
        # Vérifier le mot de passe
        password_hash = user.get('password_hash')
        
        if not password_hash:
            print("\n❌ PROBLÈME: Aucun hash de mot de passe dans la base!")
            return False
        
        print(f"\n🔍 Hash stocké: {password_hash[:50]}...")
        print(f"🔍 Mot de passe testé: {password}")
        
        # Vérifier le mot de passe
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            
            if is_valid:
                print("\n✅ MOT DE PASSE CORRECT! La connexion devrait fonctionner.")
                return True
            else:
                print("\n❌ MOT DE PASSE INCORRECT!")
                print("\n💡 Le mot de passe ne correspond pas au hash stocké.")
                return False
        except Exception as e:
            print(f"\n❌ Erreur lors de la vérification du mot de passe: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_test_user(email, password, role='admin'):
    """Créer un utilisateur de test"""
    print("\n" + "="*60)
    print(f"➕ CRÉATION D'UN UTILISATEUR DE TEST")
    print("="*60 + "\n")
    
    try:
        # Vérifier si l'utilisateur existe déjà
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if response.data:
            print(f"⚠️  L'utilisateur {email} existe déjà!")
            return response.data[0]
        
        # Hasher le mot de passe
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Créer l'utilisateur
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'is_active': True,
            'company_name': f'Test {role.title()}',
            'full_name': f'Test {role.title()} User'
        }
        
        response = supabase.table('users').insert(user_data).execute()
        
        if response.data:
            print(f"✅ Utilisateur créé avec succès!")
            print(f"   Email: {email}")
            print(f"   Mot de passe: {password}")
            print(f"   Rôle: {role}")
            return response.data[0]
        else:
            print(f"❌ Erreur lors de la création")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == "__main__":
    print("\n🚀 DIAGNOSTIC DE CONNEXION - GetYourShare")
    print("="*60)
    
    # 1. Lister tous les utilisateurs
    users = list_all_users()
    
    # 2. Si pas d'utilisateurs, proposer d'en créer
    if not users:
        print("\n💡 CRÉATION D'UTILISATEURS DE TEST...")
        print("-" * 60)
        
        # Créer des utilisateurs de test pour chaque rôle
        test_users = [
            ('admin@test.com', 'admin123', 'admin'),
            ('merchant@test.com', 'merchant123', 'merchant'),
            ('influencer@test.com', 'influencer123', 'influencer'),
            ('commercial@test.com', 'commercial123', 'commercial'),
        ]
        
        for email, password, role in test_users:
            create_test_user(email, password, role)
        
        # Relister les utilisateurs
        print("\n" + "="*60)
        users = list_all_users()
    
    # 3. Tester la connexion de chaque utilisateur
    if users:
        print("\n" + "="*60)
        print("🧪 TEST DE CONNEXION POUR CHAQUE UTILISATEUR")
        print("="*60)
        
        # Définir les mots de passe de test communs
        test_passwords = {
            'admin@test.com': 'admin123',
            'merchant@test.com': 'merchant123',
            'influencer@test.com': 'influencer123',
            'commercial@test.com': 'commercial123',
        }
        
        for user in users:
            email = user.get('email')
            password = test_passwords.get(email, 'test123')
            
            test_user_login(email, password)
    
    print("\n" + "="*60)
    print("✅ DIAGNOSTIC TERMINÉ")
    print("="*60)
    print("\n💡 Si les tests montrent 'MOT DE PASSE INCORRECT', utilisez les")
    print("   identifiants de test créés ci-dessus pour vous connecter.")
    print("\n📝 Comptes de test disponibles:")
    print("   - admin@test.com / admin123")
    print("   - merchant@test.com / merchant123")
    print("   - influencer@test.com / influencer123")
    print("   - commercial@test.com / commercial123")
    print()
