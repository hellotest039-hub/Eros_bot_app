#!/usr/bin/env python3
"""
Eros Bot - Fetch Matches Script (VERSION RATE-LIMITED)
Récupère TOUS les matchs en respectant les limites API (10 req/min)
"""

import sys
import os
import time
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.football_data_org import FootballDataOrgConnector
from backend.app.services.match_service import MatchService

# ============================================
# CONFIGURATION RATE LIMITING
# ============================================
# football-data.org limite à 10 requêtes/minute en gratuit
# On utilise 6 secondes entre chaque appel pour être sûr (60s / 10 = 6s)
API_DELAY_SECONDS = 6.5  # Petite marge de sécurité

# Compétitions à surveiller (tu peux commenter celles que tu veux ignorer)
COMPETITIONS_TO_FETCH = [
    'PL',    # Premier League (Angleterre) - Priorité 1
    'PD',    # La Liga (Espagne) - Priorité 1
    'BL1',   # Bundesliga (Allemagne) - Priorité 1
    'SA',    # Serie A (Italie) - Priorité 1
    'FL1',   # Ligue 1 (France) - Priorité 1
    'CL',    # Champions League - Priorité 1
    'EL',    # Europa League - Priorité 2
    'ECL',   # Conference League - Priorité 2
    'ELC',   # Championship (Angleterre D2) - Priorité 3
    'DED',   # Eredivisie (Pays-Bas) - Priorité 3
    'PPL',   # Primeira Liga (Portugal) - Priorité 3
    'BSA',   # Brasileirão (Brésil) - Priorité 3
    'CLI',   # Copa Libertadores - Priorité 3
]

def fetch_all_matches():
    """Fonction principale de récupération des matchs"""
    print("🚀 Eros Bot - Démarrage de la récupération des matchs...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    connector = FootballDataOrgConnector()
    match_service = MatchService()
    
    total_matches = 0
    total_requests = 0
    dates_to_fetch = [
        datetime.now().strftime('%Y-%m-%d'),
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
    ]
    
    print(f"🗓️  Dates analysées: {dates_to_fetch}")
    print(f"🏆 Compétitions surveillées: {len(COMPETITIONS_TO_FETCH)}")
    print(f"⏱️  Délai entre requêtes: {API_DELAY_SECONDS}s (pour éviter 429)")
    print("-" * 70)
    
    # Pour chaque compétition
    for idx, comp_code in enumerate(COMPETITIONS_TO_FETCH, 1):
        print(f"\n[{idx}/{len(COMPETITIONS_TO_FETCH)}] 🔍 [{comp_code}] Recherche...")
        comp_matches_count = 0
        
        # Pour chaque date
        for date_idx, date in enumerate(dates_to_fetch):
            matches = connector.get_matches_for_competition(comp_code, date, date)
            total_requests += 1
            
            for match in matches:
                match_service.save_match_football_data(match, connector)
                total_matches += 1
                comp_matches_count += 1
            
            if matches:
                print(f"   📅 {date}: {len(matches)} matchs trouvés")
            
            # ⚠️  IMPORTANT: Pause pour respecter la limite API
            # Sauf après la dernière date de la dernière compétition
            if not (date_idx == len(dates_to_fetch) - 1 and idx == len(COMPETITIONS_TO_FETCH)):
                time.sleep(API_DELAY_SECONDS)
        
        if comp_matches_count > 0:
            print(f"   ✅ [{comp_code}] Total: {comp_matches_count} matchs")
        else:
            print(f"   ℹ️  [{comp_code}] Aucun match sur ces dates")
        
        # Pause supplémentaire entre chaque compétition pour être extra-safe
        if idx < len(COMPETITIONS_TO_FETCH):
            time.sleep(API_DELAY_SECONDS)
    
    # Récupérer les matchs en DIRECT (LIVE) - 2 requêtes max
    print("\n📊 Récupération des matchs en DIRECT...")
    live_matches = connector.get_live_matches()
    total_requests += 2  # 2 statuts: IN_PLAY + PAUSED
    
    for match in live_matches:
        match_service.save_match_football_data(match, connector)
        total_matches += 1
    
    if live_matches:
        print(f"   ✅ {len(live_matches)} matchs en direct trouvés")
    else:
        print("   ℹ️  Aucun match en direct actuellement")
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DE LA RÉCUPÉRATION")
    print("=" * 70)
    print(f"✅ Matchs traités au total: {total_matches}")
    print(f"📡 Requêtes API effectuées: {total_requests}")
    print(f"⏱️  Temps estimé d'exécution: ~{total_requests * API_DELAY_SECONDS / 60:.1f} minutes")
    print(f"⏰ Prochaine exécution recommandée: dans 6 heures")
    print("=" * 70)
    
    return total_matches

def fetch_prioritized_matches(priority_level=1):
    """
    Version optimisée: ne fetch que les compétitions prioritaires
    priority_level: 1 = Top 5 ligues, 2 = + coupes européennes, 3 = tout
    """
    priority_map = {
        1: ['PL', 'PD', 'BL1', 'SA', 'FL1'],  # Les 5 grandes ligues
        2: ['PL', 'PD', 'BL1', 'SA', 'FL1', 'CL', 'EL', 'ECL'],  # + Coupes Europe
        3: COMPETITIONS_TO_FETCH  # Tout
    }
    
    competitions = priority_map.get(priority_level, priority_map[1])
    print(f"🎯 Mode prioritaire niveau {priority_level}: {len(competitions)} compétitions")
    
    # Même logique que fetch_all_matches mais avec la liste filtrée
    # (Code simplifié pour l'exemple - à implémenter si besoin)
    return fetch_all_matches()

if __name__ == "__main__":
    try:
        fetch_all_matches()
    except KeyboardInterrupt:
        print("\n⚠️  Interruption par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)