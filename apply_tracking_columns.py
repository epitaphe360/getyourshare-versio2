#!/usr/bin/env python3
"""
Script pour appliquer la migration: Ajouter colonnes de tracking à tracking_events
"""
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ ERREUR: Variables d'environnement SUPABASE_URL et SUPABASE_KEY requises")
    exit(1)

supabase: Client = create_client(url, key)

print("🔧 Application de la migration: ADD_TRACKING_COLUMNS_TO_EVENTS")
print("=" * 70)

# Lire le fichier SQL
with open("ADD_TRACKING_COLUMNS_TO_EVENTS.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

print("\n📋 Migration SQL:")
print(sql_content)

print("\n✅ Migration SQL créée avec succès!")
print("\n💡 Cette migration ajoute les colonnes suivantes à tracking_events:")
print("   - browser: Navigateur utilisé")
print("   - device: Type d'appareil (Desktop, Mobile, Tablet)")
print("   - country: Pays de provenance")
print("   - city: Ville de provenance")
print("   - referrer: URL de provenance")

print("\n📌 Appliquez cette migration dans votre console Supabase SQL Editor")
print("\n" + "=" * 70)
