#!/usr/bin/env python3
"""
🧪 Eros Bot - Test API Football-Data.org
Version Android/Acode compatible
"""

import requests
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# CONFIGURATION CHARGEMENT .ENV (SPÉCIAL ACODE)
# ============================================
# Liste des chemins possibles pour trouver le fichier .env sur Android
possible_env_paths = [
    Path('/sdcard/Eros_bot_app/backend/.env'),  # Chemin principal Acode
    Path('/sdcard/Eros_bot_app/.env'),          # Racine projet
    Path('../backend/.env'),                    # Relatif depuis data_pipeline
    Path('../.env'),                            # Relatif racine
    Path('.env'),                               # Dossier courant
]

# Trouver et charger le bon fichier .env
env_loaded = False
for env_path in possible_env_paths:
    if env_path.exists():
        print(f"✅ Fichier .env trouvé : {env_path}")
        load_dotenv(dotenv_path=env_path)
        env_loaded = True
        break

if not env_loaded:
    print("❌ ATTENTION: Aucun fichier .env trouvé !")
    print("   Assure-toi que le fichier existe dans /sdcard/Eros_bot_app/backend/")

# ============================================
# RÉCUPÉRATION DES CLÉS API
# ============================================
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = os.getenv("FOOTBALL_DATA_BASE_URL", "https://api.football-data.org/v4")

# ============================================
# AFFICHAGE DU TEST
# ============================================
print("=" * 60)
print("🚀 EROS BOT - TEST API FOOTBALL-DATA.ORG")
print("=" * 60)
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔑 Clé API chargée: {'✅ OUI' if API_KEY else '❌ NON'}")
if API_KEY:
    print(f"   (Début de clé: {API_KEY[:15]}...)")
print("=" * 60)

# Si pas de clé, on arrête ici pour éviter les erreurs
if not API_KEY:
    print("\n⚠️  Impossible de continuer sans clé API valide.")
    print("   Vérifie ton fichier backend/.env et la variable FOOTBALL_DATA_API_KEY")
    sys.exit(1)

headers = {'X-Auth-Token': API_KEY}

# ============================================
# TEST 1: LISTE DES COMPÉTITIONS
# ============================================
print("\n📊 TEST 1: Compétitions accessibles")
print("-" * 60)
try:
    url = f"{BASE_URL}/competitions"
    response = requests.get(url, headers=headers, timeout=15)
    print(f"📡 Code HTTP: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        competitions = data.get('competitions', [])
        print(f"✅ SUCCÈS: {len(competitions)} compétitions disponibles")
        print("\n🏆 Championnats accessibles (Plan Gratuit):")
        for comp in competitions:
            code = comp.get('code', 'N/A')
            name = comp.get('name', 'N/A')
            print(f"   • [{code}] {name}")
    else:
        print(f"❌ ÉCHEC API: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ ERREUR: Timeout (la requête a mis trop de temps)")
except requests.exceptions.ConnectionError:
    print("❌ ERREUR: Problème de connexion internet")
except Exception as e:
    print(f"❌ ERREUR INATTENDUE: {type(e).__name__}: {e}")

# ============================================
# TEST 2: MATCHS D'AUJOURD'HUI
# ============================================
print("\n📊 TEST 2: Matchs prévus aujourd'hui")
print("-" * 60)
try:
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"{BASE_URL}/matches"
    params = {'dateFrom': today, 'dateTo': today}
    
    print(f"🔍 Recherche des matchs pour: {today}")
    response = requests.get(url, headers=headers, params=params, timeout=15)
    print(f"📡 Code HTTP: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches', [])
        print(f"✅ SUCCÈS: {len(matches)} matchs trouvés")
        
        if matches:
            print(f"\n⚽ Liste des matchs (premiers {min(5, len(matches))}):")
            for match in matches[:5]:
                home = match.get('homeTeam', {}).get('name', 'Inconnu')
                away = match.get('awayTeam', {}).get('name', 'Inconnu')
                status = match.get('status', 'UNKNOWN')
                kickoff = match.get('utcDate', 'N/A')[0:16].replace('T', ' ')
                competition = match.get('competition', {}).get('name', 'N/A')
                
                # Icône de statut
                status_icon = "🔴 LIVE" if status in ['IN_PLAY', 'PAUSED'] else "⏳" if status == 'SCHEDULED' else "✅"
                
                print(f"   {status_icon} {home} vs {away}")
                print(f"      🏆 {competition} | 🕒 {kickoff} | [{status}]")
        else:
            print("ℹ️  Aucun match prévu aujourd'hui dans les compétitions accessibles.")
            print("   (C'est normal si c'est un jour sans grands championnats)")
            print("   💡 Astuce: Modifie la date dans le code pour tester demain.")
    else:
        print(f"❌ ÉCHEC API: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ ERREUR: Timeout")
except requests.exceptions.ConnectionError:
    print("❌ ERREUR: Problème de connexion internet")
except Exception as e:
    print(f"❌ ERREUR INATTENDUE: {type(e).__name__}: {e}")

# ============================================
# TEST 3: CONNEXION SUPABASE (RAPIDE)
# ============================================
print("\n📊 TEST 3: Connexion Supabase")
print("-" * 60)
try:
    from supabase import create_client
    supa_url = os.getenv("SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_KEY")
    
    if supa_url and supa_key:
        print(f"✅ URL Supabase trouvée: {supa_url[:30]}...")
        # Test de connexion léger (pas de requête lourde)
        client = create_client(supa_url, supa_key)
        print("✅ Client Supabase initialisé avec succès")
        
        # Petit test de lecture (optionnel)
        try:
            result = client.table('matches').select('id').limit(1).execute()
            print(f"✅ Accès table 'matches' OK ({len(result.data)} ligne(s) lue(s))")
        except Exception as db_err:
            print(f"⚠️  Attention: Table 'matches' inaccessible: {db_err}")
    else:
        print("❌ Variables Supabase manquantes dans .env")
        
except ImportError:
    print("⚠️  Module 'supabase' non installé (pip install supabase)")
except Exception as e:
    print(f"❌ ERREUR SUPABASE: {type(e).__name__}: {e}")

# ============================================
# FIN DU TEST
# ============================================
print("\n" + "=" * 60)
print("✅ FIN DU TEST API")
print("=" * 60)
print("🎯 Prochaine étape: Si tout est vert, lance fetch_matches.py !")