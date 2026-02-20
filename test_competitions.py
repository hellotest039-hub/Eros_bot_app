#!/usr/bin/env python3
"""Test rapide pour vérifier l'API football-data.org"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

headers = {'X-Auth-Token': API_KEY}

# Tester la récupération des compétitions disponibles
print("🔍 Test 1: Liste des compétitions accessibles...")
url = f"{BASE_URL}/competitions"
response = requests.get(url, headers=headers)
if response.status_code == 200:
    comps = response.json().get('competitions', [])
    print(f"✅ {len(comps)} compétitions disponibles:")
    for c in comps[:10]:  # Afficher les 10 premières
        print(f"   - {c.get('code')}: {c.get('name')}")
else:
    print(f"❌ Erreur: {response.status_code} - {response.text}")

# Tester les matchs de la Premier League (PL)
print("\n🔍 Test 2: Matchs Premier League (PL) aujourd'hui...")
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
url = f"{BASE_URL}/competitions/PL/matches"
params = {'dateFrom': today, 'dateTo': today}
response = requests.get(url, headers=headers, params=params)
if response.status_code == 200:
    matches = response.json().get('matches', [])
    print(f"✅ {len(matches)} matchs PL trouvés pour {today}:")
    for m in matches:
        home = m.get('homeTeam', {}).get('name', '?')
        away = m.get('awayTeam', {}).get('name', '?')
        print(f"   ⚽ {home} vs {away} - {m.get('utcDate')}")
else:
    print(f"❌ Erreur: {response.status_code} - {response.text}")