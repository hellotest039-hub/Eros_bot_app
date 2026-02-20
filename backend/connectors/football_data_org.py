import requests
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class FootballDataOrgConnector:
    """
    Connecteur pour l'API football-data.org
    Gère la récupération des matchs, compétitions et données associées
    """
    
    def __init__(self):
        """Initialise le connecteur avec la clé API"""
        self.api_key = os.getenv("FOOTBALL_DATA_API_KEY")
        self.base_url = os.getenv("FOOTBALL_DATA_BASE_URL", "https://api.football-data.org/v4")
        
        if not self.api_key:
            print("⚠️  ATTENTION: Clé API FOOTBALL_DATA_API_KEY non trouvée dans .env")
        
        self.headers = {
            'X-Auth-Token': self.api_key
        }
    
    def get_matches_by_date(self, date_str):
        """
        Récupère les matchs pour une date donnée (endpoint global)
        ⚠️  Limité aux compétitions majeures uniquement
        """
        url = f"{self.base_url}/matches"
        params = {
            'dateFrom': date_str,
            'dateTo': date_str
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('matches', [])
        except requests.exceptions.Timeout:
            print(f"❌ Timeout API pour la date {date_str}")
            return []
        except requests.exceptions.ConnectionError:
            print(f"❌ Erreur de connexion API pour la date {date_str}")
            return []
        except Exception as e:
            print(f"❌ Erreur Football-Data.org (date): {e}")
            return []
    
    def get_matches_for_competition(self, competition_code, date_from, date_to):
        """
        Récupère les matchs pour une compétition spécifique
        ✅ RECOMMANDÉ: Plus complet que l'endpoint global
        """
        url = f"{self.base_url}/competitions/{competition_code}/matches"
        params = {
            'dateFrom': date_from,
            'dateTo': date_to
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            matches = data.get('matches', [])
            return matches
        except requests.exceptions.Timeout:
            print(f"❌ Timeout API pour la compétition {competition_code}")
            return []
        except requests.exceptions.ConnectionError:
            print(f"❌ Erreur de connexion API pour la compétition {competition_code}")
            return []
        except Exception as e:
            print(f"❌ Erreur Football-Data.org ({competition_code}): {e}")
            return []
    
    def get_live_matches(self):
        """
        Récupère les matchs en cours (IN_PLAY ou PAUSED)
        """
        all_live_matches = []
        
        # football-data.org n'accepte qu'un seul status à la fois
        for status in ['IN_PLAY', 'PAUSED']:
            url = f"{self.base_url}/matches"
            params = {'status': status}
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                matches = data.get('matches', [])
                all_live_matches.extend(matches)
                time.sleep(0.1)  # Petit délai entre les appels
            except Exception as e:
                print(f"❌ Erreur Football-Data.org Live ({status}): {e}")
        
        return all_live_matches
    
    def get_competitions(self):
        """
        Récupère la liste de toutes les compétitions accessibles
        """
        url = f"{self.base_url}/competitions"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('competitions', [])
        except Exception as e:
            print(f"❌ Erreur Football-Data.org Competitions: {e}")
            return []
    
    def get_competition_standings(self, competition_code, season=None):
        """
        Récupère le classement d'une compétition
        """
        url = f"{self.base_url}/competitions/{competition_code}/standings"
        params = {}
        if season:
            params['season'] = season
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('standings', [])
        except Exception as e:
            print(f"❌ Erreur classement ({competition_code}): {e}")
            return []
    
    def get_team_matches(self, team_id, date_from=None, date_to=None, status=None):
        """
        Récupère les matchs d'une équipe spécifique
        """
        url = f"{self.base_url}/teams/{team_id}/matches"
        params = {}
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
        if status:
            params['status'] = status
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('matches', [])
        except Exception as e:
            print(f"❌ Erreur matchs équipe ({team_id}): {e}")
            return []
    
    def map_match_status(self, status):
        """
        Mappe le statut API vers notre format interne
        """
        status_map = {
            'SCHEDULED': 'scheduled',
            'TIMED': 'scheduled',
            'IN_PLAY': 'live',
            'PAUSED': 'live',
            'FINISHED': 'finished',
            'POSTPONED': 'postponed',
            'CANCELLED': 'cancelled',
            'SUSPENDED': 'cancelled',
            'AWAITING_PENALTIES': 'live',
            'PENS': 'finished'
        }
        return status_map.get(status, 'scheduled')
    
    def extract_match_data(self, match):
        """
        Extrait et formate les données d'un match pour la base de données
        """
        try:
            home_team = match.get('homeTeam', {}).get('name', 'Unknown')
            away_team = match.get('awayTeam', {}).get('name', 'Unknown')
            
            score = match.get('score', {})
            full_time = score.get('fullTime', {})
            half_time = score.get('halfTime', {})
            
            return {
                'match_id_api': str(match.get('id')),
                'home_team': home_team,
                'away_team': away_team,
                'match_date': match.get('utcDate'),
                'league': match.get('competition', {}).get('name', 'Unknown'),
                'competition_code': match.get('competition', {}).get('code', 'UNKNOWN'),
                'status': self.map_match_status(match.get('status')),
                'home_score': full_time.get('home'),
                'away_score': full_time.get('away'),
                'home_score_ht': half_time.get('home'),
                'away_score_ht': half_time.get('away'),
                'venue': match.get('venue', 'Unknown'),
                'referee': match.get('referees', [{}])[0].get('name') if match.get('referees') else None,
                'created_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Erreur extraction données match: {e}")
            return None
    
    def test_connection(self):
        """
        Teste la connexion à l'API
        """
        try:
            url = f"{self.base_url}/competitions"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                comps = response.json().get('competitions', [])
                return {
                    'success': True,
                    'message': f'Connexion OK - {len(comps)} compétitions accessibles',
                    'competitions_count': len(comps)
                }
            elif response.status_code == 403:
                return {
                    'success': False,
                    'message': 'Clé API invalide ou expirée (403 Forbidden)',
                    'error_code': 403
                }
            elif response.status_code == 429:
                return {
                    'success': False,
                    'message': 'Limite de requêtes dépassée (429 Too Many Requests)',
                    'error_code': 429
                }
            else:
                return {
                    'success': False,
                    'message': f'Erreur HTTP {response.status_code}: {response.text}',
                    'error_code': response.status_code
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur de connexion: {str(e)}',
                'error_code': None
            }


# ============================================
# TEST RAPIDE (si exécuté directement)
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DU CONNECTEUR FOOTBALL-DATA.ORG")
    print("=" * 60)
    
    connector = FootballDataOrgConnector()
    
    # Test 1: Connexion
    print("\n📡 Test 1: Connexion API")
    result = connector.test_connection()
    if result['success']:
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Test 2: Compétitions
    print("\n🏆 Test 2: Liste des compétitions")
    comps = connector.get_competitions()
    if comps:
        print(f"   ✅ {len(comps)} compétitions trouvées")
        for c in comps[:5]:
            print(f"      • {c.get('code')}: {c.get('name')}")
    else:
        print("   ❌ Aucune compétition trouvée")
    
    # Test 3: Matchs aujourd'hui
    print("\n⚽ Test 3: Matchs aujourd'hui")
    today = datetime.now().strftime('%Y-%m-%d')
    matches = connector.get_matches_by_date(today)
    if matches:
        print(f"   ✅ {len(matches)} matchs trouvés")
        for m in matches[:3]:
            home = m.get('homeTeam', {}).get('name', '?')
            away = m.get('awayTeam', {}).get('name', '?')
            print(f"      • {home} vs {away}")
    else:
        print("   ℹ️  Aucun match aujourd'hui")
    
    # Test 4: Matchs par compétition (ECL - Conference League)
    print("\n🎯 Test 4: Conference League (ECL)")
    ecl_matches = connector.get_matches_for_competition('ECL', today, today)
    if ecl_matches:
        print(f"   ✅ {len(ecl_matches)} matchs ECL trouvés")
        for m in ecl_matches:
            home = m.get('homeTeam', {}).get('name', '?')
            away = m.get('awayTeam', {}).get('name', '?')
            print(f"      • {home} vs {away}")
    else:
        print("   ℹ️  Aucun match ECL aujourd'hui")
    
    print("\n" + "=" * 60)
    print("✅ FIN DU TEST CONNECTEUR")
    print("=" * 60)
