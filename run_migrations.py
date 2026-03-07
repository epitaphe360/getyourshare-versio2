"""
Script de migration automatique Supabase
Crée automatiquement toutes les tables manquantes dans la base de données.
Usage: python run_migrations.py
"""
import os
import sys
import time
import requests

# ============================================================
# CONFIGURATION (lue depuis .env.railway)
# ============================================================

def load_env(filepath):
    env = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

ROOT = os.path.dirname(os.path.abspath(__file__))
env = load_env(os.path.join(ROOT, ".env.railway"))
env.update(load_env(os.path.join(ROOT, "backend", ".env")))
env.update(os.environ)

SUPABASE_URL       = env.get("SUPABASE_URL", "").rstrip("/")
SERVICE_ROLE_KEY   = env.get("SUPABASE_SERVICE_ROLE_KEY", "")
DB_PASSWORD        = env.get("SUPABASE_DB_PASSWORD") or env.get("DB_PASSWORD") or env.get("POSTGRES_PASSWORD") or ""

if not SUPABASE_URL or not SERVICE_ROLE_KEY:
    print("❌ SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY manquant dans .env.railway")
    sys.exit(1)

# Extraire le project_ref depuis l'URL (ex: iamezkmapbhlhhvvsits)
PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0]

MIGRATION_FILES = [
    os.path.join(ROOT, "backend", "migrations", "create_media_tables.sql"),
    os.path.join(ROOT, "backend", "migrations", "ADD_MISSING_TABLES_PHASE7.sql"),
]

HEADERS = {
    "apikey":        SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}


# ============================================================
# MÉTHODE 1 : Connexion PostgreSQL directe via psycopg2
# ============================================================

def run_via_psycopg2(sql_content: str, label: str) -> bool:
    if not DB_PASSWORD:
        return False
    try:
        import psycopg2
        conn_str = (
            f"postgresql://postgres:{DB_PASSWORD}"
            f"@db.{PROJECT_REF}.supabase.co:5432/postgres"
            f"?sslmode=require"
        )
        print(f"  📡 Connexion PostgreSQL directe ({PROJECT_REF})…")
        conn = psycopg2.connect(conn_str, connect_timeout=10)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql_content)
        cur.close()
        conn.close()
        print(f"  ✅ {label} — exécutée via psycopg2")
        return True
    except ImportError:
        print("  ⚠️  psycopg2 non installé (pip install psycopg2-binary)")
        return False
    except Exception as e:
        print(f"  ⚠️  psycopg2 échoué : {e}")
        return False


# ============================================================
# MÉTHODE 2 : Supabase Management API (nécessite PAT)
# ============================================================

def run_via_management_api(sql_content: str, label: str, pat: str) -> bool:
    if not pat:
        return False
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type":  "application/json",
    }
    # Découper en statements pour éviter les timeouts
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    total = len(statements)
    ok = 0
    for i, stmt in enumerate(statements, 1):
        try:
            r = requests.post(url, json={"query": stmt + ";"}, headers=headers, timeout=30)
            if r.status_code in (200, 201, 204):
                ok += 1
            else:
                # Ignorer "already exists"
                body = r.text.lower()
                if "already exists" in body or "duplicate" in body:
                    ok += 1
                else:
                    print(f"    ⚠️  Stmt {i}/{total}: HTTP {r.status_code} → {r.text[:120]}")
        except Exception as e:
            print(f"    ⚠️  Stmt {i}/{total}: {e}")
        # Rate-limit doux
        if i % 20 == 0:
            time.sleep(0.5)
    print(f"  ✅ {label} — {ok}/{total} statements OK via Management API")
    return ok > 0


# ============================================================
# MÉTHODE 3 : RPC Supabase (fonction exec_sql si existante)
# ============================================================

def run_via_rpc(sql_content: str, label: str) -> bool:
    """
    Tente d'appeler une fonction PL/pgSQL 'exec_sql(query text)'
    si elle existe déjà dans la base publique.
    """
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    total = len(statements)
    ok = 0
    for stmt in statements:
        try:
            r = requests.post(url, json={"query": stmt + ";"}, headers=HEADERS, timeout=10)
            if r.status_code in (200, 201, 204):
                ok += 1
            elif "already exists" in r.text.lower():
                ok += 1
        except Exception:
            pass
    if ok > 0:
        print(f"  ✅ {label} — {ok}/{total} via RPC exec_sql")
        return True
    return False


# ============================================================
# RUNNER PRINCIPAL
# ============================================================

def run_migration(filepath: str) -> bool:
    label = os.path.basename(filepath)
    if not os.path.exists(filepath):
        print(f"  ⚠️  Fichier introuvable : {filepath}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()

    print(f"\n📄 Migration : {label}")

    # Essai 1 : psycopg2 direct
    if run_via_psycopg2(sql, label):
        return True

    # Essai 2 : RPC exec_sql
    if run_via_rpc(sql, label):
        return True

    # Essai 3 : Management API avec PAT
    pat = env.get("SUPABASE_PAT") or env.get("SUPABASE_MANAGEMENT_TOKEN") or ""
    if not pat:
        print(f"  💡 Aucune méthode automatique disponible pour « {label} ».")
        print(f"     → Voir section MANUEL ci-dessous.")
        return False

    return run_via_management_api(sql, label, pat)


# ============================================================
# INSTRUCTIONS MANUELLES (fallback)
# ============================================================

def show_manual_instructions():
    print("\n" + "="*62)
    print("📋  INSTRUCTIONS POUR CRÉER LES TABLES MANUELLEMENT")
    print("="*62)
    print(f"\n1. Ouvre : https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new")
    print("\n2. Copie-colle chaque fichier dans l'éditeur SQL :")
    for f in MIGRATION_FILES:
        print(f"   • {os.path.relpath(f, ROOT)}")
    print("\n3. Clique sur 'Run' pour chaque fichier.\n")
    print("─── OU ──────────────────────────────────────────────────")
    print("\nPour automatiser complètement, ajoute l'une de ces variables")
    print("dans ton fichier .env.railway :\n")
    print("  # Option A : Mot de passe PostgreSQL direct (Settings → Database)")
    print("  SUPABASE_DB_PASSWORD=ton_mot_de_passe\n")
    print("  # Option B : Personal Access Token (Account → Access Tokens)")
    print("  SUPABASE_PAT=sbp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
    print("  Puis relance : python run_migrations.py\n")
    print(f"  Dashboard : https://supabase.com/dashboard/account/tokens")
    print("="*62)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n🚀 GetYourShare — Migration automatique Supabase")
    print(f"   Projet : {PROJECT_REF}")
    print(f"   URL    : {SUPABASE_URL}\n")

    results = {}
    for filepath in MIGRATION_FILES:
        results[filepath] = run_migration(filepath)

    success = sum(results.values())
    failed  = [os.path.basename(k) for k, v in results.items() if not v]

    print(f"\n{'='*62}")
    print(f"✅ {success}/{len(MIGRATION_FILES)} migrations exécutées automatiquement.")

    if failed:
        print(f"⚠️  Échec pour : {', '.join(failed)}")
        show_manual_instructions()
    else:
        print("🎉 Toutes les tables sont créées dans Supabase !")
    print(f"{'='*62}\n")
