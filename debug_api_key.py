#!/usr/bin/env python3
"""
🔍 Debug Clé API Football-Data.org
Test minimal pour identifier le problème 401
"""

import requests
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("🔍 DEBUG CLÉ API FOOTBALL-DATA.ORG")
print("=" * 60)

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

# Récupérer la clé
api_key = os.getenv("FOOTBALL_DATA_API_KEY")
print(f"\n🔑 Clé API chargée: {'✅ OUI' if api_key else '❌ NON'}")

if api_key:
    print(f"   Longueur: {len(api_key)} caractères")
    print(f"   Début: {api_key[:20]}...")
    print(f"   Fin: ...{api_key[-20:]}")
    
    # Vérifier format (doit être alphanumérique, ~64 chars)
    if len(api_key) < 50:
        print("   ⚠️  ATTENTION: Clé trop courte !")
    if ' ' in api_key or '\n' in api_key:
        print("   ⚠️  ATTENTION: Clé contient espaces ou sauts de ligne !")
else:
    print("❌ La clé est vide dans .env")
    print("💡 Vérifie: FOOTBALL_DATA_API_KEY=ta_clé_ici (sans espaces)")

# Test 1: Appel minimal à l'API
print("\n" + "-" * 60)
print("📡 TEST 1: Appel API minimal")
print("-" * 60)

if api_key:
    url = "https://api.football-data.org/v4/competitions"
    headers = {'X-Auth-Token': api_key}
    
    print(f"URL: {url}")
    print(f"Header: X-Auth-Token: {api_key[:10]}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n📊 Réponse HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCÈS ! La clé fonctionne !")
            data = response.json()
            print(f"🏆 Compétitions accessibles: {len(data.get('competitions', []))}")
            
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - Clé invalide")
            print("\n💡 Solutions:")
            print("   1. Vérifie que ta clé est correcte sur football-data.org")
            print("   2. Regénère une nouvelle clé dans ton dashboard")
            print("   3. Copie-la SANS espaces ni sauts de ligne")
            print("   4. Redémarre ton script après mise à jour du .env")
            
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Clé valide mais accès refusé")
            print("💡 Ta clé est bonne mais peut-être expirée ou suspendue")
            
        elif response.status_code == 429:
            print("❌ 429 Too Many Requests - Limite dépassée")
            print("💡 Attends 1 minute et réessaie")
            
        else:
            print(f"❌ Autre erreur: {response.status_code}")
            print(f"Réponse: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Problème de connexion internet")
    except Exception as e:
        print(f"❌ Erreur: {type(e).__name__}: {e}")
else:
    print("⏭️  Test API ignoré (pas de clé)")

# Test 2: Vérifier le header dans le connecteur
print("\n" + "-" * 60)
print("🔧 TEST 2: Vérification du connecteur")
print("-" * 60)

try:
    from connectors.football_data_org import FootballDataOrgConnector
    connector = FootballDataOrgConnector()
    
    print(f"✅ Connecteur importé avec succès")
    print(f"🔑 Clé dans connector: {'✅' if connector.api_key else '❌'}")
    print(f"📋 Headers générés: {connector.headers}")
    
    # Vérifier format du header
    expected_header = {'X-Auth-Token': api_key}
    if connector.headers == expected_header:
        print("✅ Format du header: CORRECT")
    else:
        print("⚠️  Format du header: DIFFÉRENT de l'attendu")
        print(f"   Attendu: {expected_header}")
        print(f"   Obtenu:  {connector.headers}")
        
except ImportError as e:
    print(f"❌ Impossible d'importer le connecteur: {e}")
except Exception as e:
    print(f"❌ Erreur connecteur: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("✅ FIN DU DEBUG")
print("=" * 60)