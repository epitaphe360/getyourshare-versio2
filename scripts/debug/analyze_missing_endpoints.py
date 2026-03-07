"""
Script d'analyse des endpoints manquants
Analyse tous les appels API du frontend et vérifie leur existence dans le backend
"""

import re
import os
from pathlib import Path
from collections import defaultdict

# Chemins
FRONTEND_DIR = Path("frontend/src")
BACKEND_FILE = Path("backend/server.py")

def extract_api_calls_from_file(filepath):
    """Extrait tous les appels API d'un fichier JS/JSX"""
    api_calls = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Patterns pour détecter les appels API
            patterns = [
                r"api\.(get|post|put|patch|delete)\(['\"]([^'\"]+)['\"]",
                r"axios\.(get|post|put|patch|delete)\(['\"]([^'\"]+)['\"]",
                r"fetch\(['\"]([^'\"]+)['\"]"
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    if 'fetch' in pattern:
                        url = match.group(1)
                        method = 'GET'
                    else:
                        method = match.group(1).upper()
                        url = match.group(2)
                    
                    # Nettoyer l'URL (enlever le domaine si présent)
                    if 'http://localhost' in url or '${API_URL}' in url:
                        url = re.sub(r'.*(http://localhost:\d+|(\$\{API_URL\}))', '', url)
                    
                    # Garder seulement les endpoints /api/...
                    if url.startswith('/api/'):
                        api_calls.append({
                            'method': method,
                            'endpoint': url,
                            'file': str(filepath)
                        })
    except Exception as e:
        print(f"Erreur lecture {filepath}: {e}")
    
    return api_calls

def extract_backend_endpoints(backend_file):
    """Extrait tous les endpoints définis dans le backend"""
    endpoints = []
    
    try:
        with open(backend_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Pattern pour les décorateurs FastAPI
            pattern = r'@app\.(get|post|put|patch|delete)\(["\']([^"\']+)["\']\)'
            
            matches = re.finditer(pattern, content)
            for match in matches:
                method = match.group(1).upper()
                endpoint = match.group(2)
                endpoints.append({
                    'method': method,
                    'endpoint': endpoint
                })
    except Exception as e:
        print(f"Erreur lecture backend: {e}")
    
    return endpoints

def normalize_endpoint(endpoint):
    """Normalise un endpoint pour la comparaison"""
    # Remplacer les paramètres dynamiques par un placeholder
    normalized = re.sub(r'\{[^}]+\}', '{id}', endpoint)
    normalized = re.sub(r'/[a-f0-9-]{36}', '/{id}', normalized)  # UUID
    normalized = re.sub(r'/\d+', '/{id}', normalized)  # Nombres
    return normalized

def main():
    print("🔍 ANALYSE DES ENDPOINTS MANQUANTS\n")
    print("="*80)
    
    # 1. Extraire tous les appels API du frontend
    print("\n📂 Analyse du frontend...")
    all_api_calls = []
    
    for root, dirs, files in os.walk(FRONTEND_DIR):
        for file in files:
            if file.endswith(('.js', '.jsx')):
                filepath = Path(root) / file
                calls = extract_api_calls_from_file(filepath)
                all_api_calls.extend(calls)
    
    print(f"   ✅ {len(all_api_calls)} appels API trouvés")
    
    # 2. Extraire tous les endpoints du backend
    print("\n📂 Analyse du backend...")
    backend_endpoints = extract_backend_endpoints(BACKEND_FILE)
    print(f"   ✅ {len(backend_endpoints)} endpoints trouvés")
    
    # 3. Grouper les appels par endpoint
    calls_by_endpoint = defaultdict(list)
    for call in all_api_calls:
        key = f"{call['method']} {normalize_endpoint(call['endpoint'])}"
        calls_by_endpoint[key].append(call)
    
    # 4. Grouper les endpoints backend
    backend_set = set()
    for endpoint in backend_endpoints:
        key = f"{endpoint['method']} {normalize_endpoint(endpoint['endpoint'])}"
        backend_set.add(key)
    
    # 5. Trouver les endpoints manquants
    print("\n" + "="*80)
    print("🔴 ENDPOINTS MANQUANTS\n")
    
    missing_count = 0
    missing_endpoints = []
    
    for endpoint_key, calls in sorted(calls_by_endpoint.items()):
        if endpoint_key not in backend_set:
            missing_count += 1
            missing_endpoints.append({
                'key': endpoint_key,
                'calls': calls
            })
            
            method, endpoint = endpoint_key.split(' ', 1)
            print(f"\n{missing_count}. {method} {endpoint}")
            print(f"   📍 Appelé dans {len(calls)} endroit(s):")
            
            # Afficher les fichiers uniques
            files = set(call['file'] for call in calls)
            for file in sorted(files):
                short_path = file.replace('frontend\\src\\', '')
                print(f"      • {short_path}")
    
    # 6. Statistiques
    print("\n" + "="*80)
    print("📊 STATISTIQUES\n")
    print(f"   Total appels API frontend: {len(all_api_calls)}")
    print(f"   Endpoints uniques frontend: {len(calls_by_endpoint)}")
    print(f"   Endpoints backend: {len(backend_set)}")
    print(f"   ❌ Endpoints MANQUANTS: {missing_count}")
    print(f"   ✅ Endpoints OK: {len(calls_by_endpoint) - missing_count}")
    
    # 7. Endpoints les plus critiques (appelés dans plusieurs fichiers)
    if missing_endpoints:
        print("\n" + "="*80)
        print("⚠️  ENDPOINTS PRIORITAIRES (appelés dans 3+ fichiers)\n")
        
        critical = [ep for ep in missing_endpoints if len(set(c['file'] for c in ep['calls'])) >= 3]
        
        for i, ep in enumerate(sorted(critical, key=lambda x: len(set(c['file'] for c in x['calls'])), reverse=True), 1):
            method, endpoint = ep['key'].split(' ', 1)
            file_count = len(set(c['file'] for c in ep['calls']))
            print(f"{i}. {method} {endpoint}")
            print(f"   🔥 Utilisé dans {file_count} fichiers différents")
    
    # 8. Générer la liste pour correction
    print("\n" + "="*80)
    print("📝 LISTE DES ENDPOINTS À CRÉER\n")
    
    for i, ep in enumerate(missing_endpoints, 1):
        method, endpoint = ep['key'].split(' ', 1)
        print(f"{i}. {method} {endpoint}")
    
    print("\n" + "="*80)
    print(f"\n✅ Analyse terminée! {missing_count} endpoints à créer.\n")

if __name__ == "__main__":
    main()
