#!/usr/bin/env python3
"""
🔍 Eros Bot - Test COMPLET Tous les Matchs Disponibles
Affiche TOUTES les compétitions et leurs matchs jour par jour
"""

import requests
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# CHARGEMENT .ENV (Spécial Acode Android)
# ============================================
possible_env_paths = [
    Path('/sdcard/Eros_bot_app/backend/.env'),
    Path('/sdcard/Eros_bot_app/.env'),
    Path('../backend/.env'),
    Path('../.env'),
    Path('.env'),
]

env_loaded = False
for env_path in possible_env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✅ .env chargé depuis: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print("❌ ERREUR: Fichier .env non trouvé !")
    sys.exit(1)

# ============================================
# CONFIGURATION API
# ============================================
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

if not API_KEY:
    print("❌ ERREUR: Clé API non trouvée dans .env")
    sys.exit(1)

headers = {'X-Auth-Token': API_KEY}

# ============================================
# FONCTIONS UTILITAIRES
# ============================================
def get_all_competitions():
    """Récupère toutes les compétitions accessibles"""
    url = f"{BASE_URL}/competitions"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('competitions', [])
    except Exception as e:
        print(f"❌ Erreur compétitions: {e}")
    return []

def get_matches_for_competition(competition_code, date_from, date_to):
    """Récupère les matchs pour une compétition et période données"""
    url = f"{BASE_URL}/competitions/{competition_code}/matches"
    params = {'dateFrom': date_from, 'dateTo': date_to}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            return response.json().get('matches', [])
    except Exception as e:
        print(f"❌ Erreur matchs {competition_code}: {e}")
    return []

def get_all_matches_by_date(date_from, date_to):
    """Récupère TOUS les matchs sans filtrer par compétition"""
    url = f"{BASE_URL}/matches"
    params = {'dateFrom': date_from, 'dateTo': date_to}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            return response.json().get('matches', [])
    except Exception as e:
        print(f"❌ Erreur matchs globaux: {e}")
    return []

def format_match(match):
    """Formate l'affichage d'un match"""
    home = match.get('homeTeam', {}).get('name', '???')
    away = match.get('awayTeam', {}).get('name', '???')
    status = match.get('status', 'UNKNOWN')
    date = match.get('utcDate', '???')[0:16].replace('T', ' ')
    competition = match.get('competition', {}).get('name', '???')
    
    status_icon = {"IN_PLAY": "🔴", "PAUSED": "⏸️", "SCHEDULED": "⏳", "FINISHED": "✅"}.get(status, "⚪")
    
    return f"   {status_icon} {home} vs {away}\n      🏆 {competition} | 🕒 {date} | [{status}]"

# ============================================
# AFFICHAGE PRINCIPAL
# ============================================
print("=" * 70)
print("🔍 EROS BOT - TEST COMPLET TOUS LES MATCHS DISPONIBLES")
print("=" * 70)
print(f"📅 Date du test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔑 API: football-data.org v4")
print(f"🎯 Objectif: Voir TOUS les matchs accessibles aujourd'hui")
print("=" * 70)

# ============================================
# ÉTAPE 1: LISTE TOUTES LES COMPÉTITIONS
# ============================================
print("\n" + "=" * 70)
print("📋 ÉTAPE 1: TOUTES LES COMPÉTITIONS ACCESSIBLES")
print("=" * 70)

competitions = get_all_competitions()
print(f"\n✅ {len(competitions)} compétitions accessibles:\n")

for i, comp in enumerate(competitions, 1):
    code = comp.get('code', 'N/A')
    name = comp.get('name', 'N/A')
    country = comp.get('area', {}).get('name', 'N/A')
    print(f"   {i:2}. [{code:5}] {name:35} ({country})")

# ============================================
# ÉTAPE 2: MATCHS GLOBAUX (TOUTES COMPÉTITIONS)
# ============================================
print("\n" + "=" * 70)
print("📊 ÉTAPE 2: TOUS LES MATCHS AUJOURD'HUI (Vue Globale)")
print("=" * 70)

today = datetime.now().strftime('%Y-%m-%d')
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
day_after = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

print(f"\n🗓️  Période analysée: {today} au {day_after}\n")

# Matchs aujourd'hui
print(f"📅 MATCHS DU JOUR ({today}):")
print("-" * 70)
global_matches_today = get_all_matches_by_date(today, today)
if global_matches_today:
    for match in global_matches_today:
        print(format_match(match))
    print(f"\n✅ Total: {len(global_matches_today)} matchs aujourd'hui")
else:
    print("   ❌ Aucun match trouvé aujourd'hui dans les compétitions accessibles")

# Matchs demain
print(f"\n📅 MATCHS DE DEMAIN ({tomorrow}):")
print("-" * 70)
global_matches_tomorrow = get_all_matches_by_date(tomorrow, tomorrow)
if global_matches_tomorrow:
    for match in global_matches_tomorrow:
        print(format_match(match))
    print(f"\n✅ Total: {len(global_matches_tomorrow)} matchs demain")
else:
    print("   ❌ Aucun match trouvé demain dans les compétitions accessibles")

# Matchs après-demain
print(f"\n📅 MATCHS D'APRÈS-DEMAIN ({day_after}):")
print("-" * 70)
global_matches_day_after = get_all_matches_by_date(day_after, day_after)
if global_matches_day_after:
    for match in global_matches_day_after:
        print(format_match(match))
    print(f"\n✅ Total: {len(global_matches_day_after)} matchs après-demain")
else:
    print("   ❌ Aucun match trouvé après-demain dans les compétitions accessibles")

# ============================================
# ÉTAPE 3: RECHERCHE SPÉCIALE CONFERENCE LEAGUE
# ============================================
print("\n" + "=" * 70)
print("🏆 ÉTAPE 3: RECHERCHE SPÉCIALE CONFERENCE LEAGUE")
print("=" * 70)

# Conference League = ECL dans football-data.org
ecl_matches = get_matches_for_competition('ECL', today, day_after)
if ecl_matches:
    print(f"\n✅ CONFERENCE LEAGUE TROUVÉE: {len(ecl_matches)} matchs!")
    for match in ecl_matches:
        print(format_match(match))
else:
    print("\n❌ Aucun match Conference League trouvé pour ces dates")
    print("   (Vérifie si des matchs ECL sont programmés ces jours-ci)")

# ============================================
# ÉTAPE 4: RÉCAPITULATIF PAR COMPÉTITION
# ============================================
print("\n" + "=" * 70)
print("📊 ÉTAPE 4: RÉCAPITULATIF PAR COMPÉTITION (3 prochains jours)")
print("=" * 70)

print(f"\n{'Compétition':<35} | {'Auj.':<6} | {'Dem.':<6} | {'Après':<6} | {'Total':<6}")
print("-" * 70)

total_all_competitions = 0
for comp in competitions:
    code = comp.get('code', 'N/A')
    name = comp.get('name', 'N/A')[:33]
    
    # Variables locales pour ne pas écraser les globales
    comp_matches_today = len(get_matches_for_competition(code, today, today))
    comp_matches_tomorrow = len(get_matches_for_competition(code, tomorrow, tomorrow))
    comp_matches_day_after = len(get_matches_for_competition(code, day_after, day_after))
    
    comp_total = comp_matches_today + comp_matches_tomorrow + comp_matches_day_after
    total_all_competitions += comp_total
    
    if comp_total > 0:
        print(f"{name:<35} | {comp_matches_today:^6} | {comp_matches_tomorrow:^6} | {comp_matches_day_after:^6} | {comp_total:^6}")

print("-" * 70)
print(f"{'TOTAL GÉNÉRAL':<35} | {len(global_matches_today):^6} | {len(global_matches_tomorrow):^6} | {len(global_matches_day_after):^6} | {total_all_competitions:^6}")

# ============================================
# ÉTAPE 5: CONNEXION SUPABASE
# ============================================
print("\n" + "=" * 70)
print("💾 ÉTAPE 5: VÉRIFICATION BASE DE DONNÉES SUPABASE")
print("=" * 70)

try:
    from supabase import create_client
    supa_url = os.getenv("SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_KEY")
    
    if supa_url and supa_key:
        client = create_client(supa_url, supa_key)
        
        # Compter les matchs en base
        result = client.table('matches').select('id', count='exact').execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        
        print(f"✅ Connexion Supabase: OK")
        print(f"📊 Matchs en base de données: {count}")
        
        # Afficher les 5 derniers matchs ajoutés
        recent = client.table('matches').select('home_team,away_team,match_date,league').order('created_at', desc=True).limit(5).execute()
        if recent.data:
            print(f"\n📋 5 derniers matchs en base:")
            for m in recent.data:
                print(f"   ⚽ {m.get('home_team', '?')} vs {m.get('away_team', '?')} ({m.get('league', '?')})")
    else:
        print("⚠️  Variables Supabase non configurées")
        
except Exception as e:
    print(f"❌ Erreur Supabase: {e}")

# ============================================
# CONCLUSION
# ============================================
print("\n" + "=" * 70)
print("✅ FIN DU TEST COMPLET")
print("=" * 70)

total_matches = len(global_matches_today) + len(global_matches_tomorrow) + len(global_matches_day_after)
print(f"\n📊 RÉSUMÉ:")
print(f"   • Compétitions accessibles: {len(competitions)}")
print(f"   • Matchs aujourd'hui: {len(global_matches_today)}")
print(f"   • Matchs demain: {len(global_matches_tomorrow)}")
print(f"   • Matchs après-demain: {len(global_matches_day_after)}")
print(f"   • TOTAL (3 jours): {total_matches}")

if total_matches == 0:
    print(f"\n⚠️  ATTENTION: Aucun match trouvé sur 3 jours!")
    print(f"   Causes possibles:")
    print(f"   1. Pas de matchs programmés ces dates (trêve, vacances...)")
    print(f"   2. Conference League non incluse dans le plan gratuit")
    print(f"   3. Problème de clé API")
    print(f"\n💡 Solution: Tester avec des dates connues (week-end de championnat)")
else:
    print(f"\n🎯 Tout fonctionne! Prêt pour les prédictions IA!")

print("=" * 70)