#!/usr/bin/env python3
"""
🔍 Eros Bot - Debug Supabase Complet
Vérifie la connexion, les tables, les permissions et les données
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Charger .env
possible_paths = [
    Path('/sdcard/Eros_bot_app/backend/.env'),
    Path('/sdcard/Eros_bot_app/.env'),
    Path('../backend/.env'),
    Path('.env'),
]

for p in possible_paths:
    if p.exists():
        load_dotenv(dotenv_path=p)
        print(f"✅ .env chargé: {p}")
        break
else:
    print("❌ .env non trouvé !")
    exit(1)

print("=" * 70)
print("🔍 DEBUG SUPABASE - EROS BOT")
print("=" * 70)

# Récupérer les credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"\n📡 URL Supabase: {SUPABASE_URL[:40]}...")
print(f"🔑 Clé API: {SUPABASE_KEY[:30]}...")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERREUR: Credentials Supabase manquants dans .env")
    exit(1)

# ============================================
# TEST 1: CONNEXION DE BASE
# ============================================
print("\n" + "=" * 70)
print("TEST 1: Connexion Supabase")
print("=" * 70)

try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Client Supabase créé avec succès")
except Exception as e:
    print(f"❌ ERREUR DE CONNEXION: {type(e).__name__}: {e}")
    print("\n💡 Solution: Vérifie que supabase est installé")
    print("   Commande: pip install supabase")
    exit(1)

# ============================================
# TEST 2: LISTE DES TABLES
# ============================================
print("\n" + "=" * 70)
print("TEST 2: Liste des tables disponibles")
print("=" * 70)

try:
    # Requête pour lister les tables (fonctionne avec la plupart des configs Supabase)
    result = supabase.rpc('get_tables').execute()
    print(f"✅ Tables trouvées: {result.data}")
except Exception as e:
    print(f"⚠️  Impossible de lister les tables: {e}")
    print("   (C'est normal si la fonction rpc n'existe pas)")

# ============================================
# TEST 3: VÉRIFIER LA TABLE 'matches'
# ============================================
print("\n" + "=" * 70)
print("TEST 3: Table 'matches'")
print("=" * 70)

try:
    # Essayer de compter les lignes
    result = supabase.table('matches').select('*', count='exact').execute()
    count = result.count if hasattr(result, 'count') else len(result.data)
    print(f"✅ Table 'matches' existe")
    print(f"📊 Nombre de lignes: {count}")
except Exception as e:
    print(f"❌ ERREUR avec la table 'matches': {type(e).__name__}: {e}")
    print("\n💡 Causes possibles:")
    print("   1. La table n'existe pas → Crée-la dans Supabase Table Editor")
    print("   2. Row Level Security (RLS) bloque l'accès")
    print("   3. La clé API n'a pas les permissions")

# ============================================
# TEST 4: INSÉRER UN MATCH TEST
# ============================================
print("\n" + "=" * 70)
print("TEST 4: Insertion d'un match test")
print("=" * 70)

test_match = {
    'match_id_api': f'test_{datetime.now().timestamp()}',
    'home_team': 'Equipe Test Domicile',
    'away_team': 'Equipe Test Extérieur',
    'match_date': datetime.now().isoformat(),
    'league': 'Test League',
    'status': 'scheduled',
    'home_score': None,
    'away_score': None,
    'created_at': datetime.now().isoformat()
}

print(f"📝 Données à insérer:")
for k, v in test_match.items():
    print(f"   {k}: {v}")

try:
    result = supabase.table('matches').insert(test_match).execute()
    print(f"\n✅ INSERTION RÉUSSIE !")
    print(f"📊 Résultat: {result.data}")
    
    # Vérifier qu'on peut le lire
    verify = supabase.table('matches').select('*').eq('match_id_api', test_match['match_id_api']).execute()
    if verify.data and len(verify.data) > 0:
        print(f"✅ LECTURE CONFIRMÉE: Le match est visible dans la base")
    else:
        print(f"⚠️  ATTENTION: Insertion OK mais lecture impossible")
        print(f"   → Problème de Row Level Security (RLS)")
        
except Exception as e:
    print(f"\n❌ ÉCHEC DE L'INSERTION: {type(e).__name__}: {e}")
    error_msg = str(e)
    
    if '42501' in error_msg or 'permission' in error_msg.lower():
        print("\n💡 ERREUR DE PERMISSION détectée !")
        print("   Solution: Désactiver RLS ou ajouter une policy")
    elif 'relation' in error_msg.lower():
        print("\n💡 TABLE N'EXISTE PAS détectée !")
        print("   Solution: Créer la table dans Supabase Table Editor")
    else:
        print(f"\n💡 Autre erreur: {error_msg}")

# ============================================
# TEST 5: VÉRIFIER ROW LEVEL SECURITY (RLS)
# ============================================
print("\n" + "=" * 70)
print("TEST 5: Row Level Security (RLS)")
print("=" * 70)

print("\n⚠️  IMPORTANT: Supabase active RLS par défaut !")
print("\n📋 Pour désactiver RLS sur la table 'matches':")
print("   1. Va sur supabase.com → Ton projet → Table Editor")
print("   2. Clique sur la table 'matches'")
print("   3. Clique sur les 3 points ⋮ → Edit table")
print("   4. Désactive 'Row Level Security' OU")
print("   5. Ajoute une policy: CREATE POLICY avec 'SELECT/INSERT ALL'")
print("\n🔗 Ou exécute ce SQL dans SQL Editor:")
print("""
   ALTER TABLE matches DISABLE ROW LEVEL SECURITY;
   
   -- OU pour garder RLS mais permettre tout:
   CREATE POLICY "Allow all" ON matches
   FOR ALL USING (true) WITH CHECK (true);
""")

# ============================================
# TEST 6: RÉCUPÉRER LES DERNIERS MATCHS
# ============================================
print("\n" + "=" * 70)
print("TEST 6: Récupération des 10 derniers matchs")
print("=" * 70)

try:
    result = supabase.table('matches').select('*').order('created_at', desc=True).limit(10).execute()
    
    if result.data and len(result.data) > 0:
        print(f"✅ {len(result.data)} matchs trouvés:\n")
        for i, m in enumerate(result.data, 1):
            home = m.get('home_team', '?')
            away = m.get('away_team', '?')
            date = m.get('match_date', '?')[:10] if m.get('match_date') else '?'
            status = m.get('status', '?')
            print(f"   {i}. {home} vs {away} - {date} [{status}]")
    else:
        print("ℹ️  Aucun match dans la base de données")
        print("💡 C'est normal si tu viens de créer la table")
        
except Exception as e:
    print(f"❌ ERREUR: {type(e).__name__}: {e}")

# ============================================
# CONCLUSION
# ============================================
print("\n" + "=" * 70)
print("✅ FIN DU DEBUG SUPABASE")
print("=" * 70)

print("\n📋 CHECKLIST À VÉRIFIER:")
print("   ☐ 1. La table 'matches' existe dans Supabase")
print("   ☐ 2. Les colonnes correspondent au code (voir schéma ci-dessous)")
print("   ☐ 3. Row Level Security (RLS) est désactivé OU policies configurées")
print("   ☐ 4. La clé API (anon) a les permissions INSERT/SELECT")
print("   ☐ 5. Le fichier .env contient les bonnes URLs et clés")

print("\n📊 SCHÉMA DE LA TABLE 'matches' RECOMMANDÉ:")
print("""
   CREATE TABLE matches (
       id BIGSERIAL PRIMARY KEY,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       match_id_api TEXT UNIQUE,
       home_team TEXT,
       away_team TEXT,
       match_date TIMESTAMPTZ,
       league TEXT,
       status TEXT,
       home_score INTEGER,
       away_score INTEGER
   );
""")

print("=" * 70)