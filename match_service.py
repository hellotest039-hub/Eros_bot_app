from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class MatchService:
    """
    Service de gestion des matchs dans Supabase
    Gère l'insertion, la mise à jour et la récupération des matchs
    """
    
    def __init__(self):
        """Initialise la connexion Supabase"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            print("⚠️  ATTENTION: Variables Supabase non configurées dans .env")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Connexion Supabase initialisée")
        except Exception as e:
            print(f"❌ Erreur connexion Supabase: {e}")
            self.supabase = None
    
    def save_match(self, match_data):
        """
        Enregistre un match dans la base de données (format API-Football)
        """
        try:
            if not self.supabase:
                print("❌ Supabase non connecté")
                return None
            
            data = {
                'match_id_api': str(match_data.get('fixture', {}).get('id')),
                'home_team': match_data.get('teams', {}).get('home', {}).get('name'),
                'away_team': match_data.get('teams', {}).get('away', {}).get('name'),
                'match_date': match_data.get('fixture', {}).get('date'),
                'league': match_data.get('league', {}).get('name'),
                'status': self._map_status(match_data.get('fixture', {}).get('status', {}).get('short')),
                'home_score': match_data.get('goals', {}).get('home'),
                'away_score': match_data.get('goals', {}).get('away'),
                'created_at': datetime.now().isoformat()
            }
            
            # Vérifier si le match existe déjà
            existing = self.supabase.table('matches').select('id').eq('match_id_api', data['match_id_api']).execute()
            
            if existing.data and len(existing.data) > 0:
                result = self.supabase.table('matches').update(data).eq('match_id_api', data['match_id_api']).execute()
                print(f"✅ Match mis à jour: {data['home_team']} vs {data['away_team']}")
            else:
                result = self.supabase.table('matches').insert(data).execute()
                print(f"✅ Match ajouté: {data['home_team']} vs {data['away_team']}")
            
            return result.data
        except Exception as e:
            print(f"❌ Erreur Supabase: {e}")
            return None
    
    def save_match_football_data(self, match_data, connector):
        """
        Enregistre un match depuis football-data.org
        ✅ MÉTHODE PRINCIPALE POUR TON BOT ACTUEL
        """
        try:
            if not self.supabase:
                print("❌ Supabase non connecté")
                return None
            
            # Extraire les données du match
            home_team = match_data.get('homeTeam', {}).get('name', 'Unknown')
            away_team = match_data.get('awayTeam', {}).get('name', 'Unknown')
            
            # Récupérer les scores (peut être None si match pas commencé)
            score = match_data.get('score', {})
            full_time = score.get('fullTime', {})
            half_time = score.get('halfTime', {})
            
            # Récupérer les infos de compétition
            competition = match_data.get('competition', {})
            league_name = competition.get('name', 'Unknown')
            competition_code = competition.get('code', 'UNKNOWN')
            
            data = {
                'match_id_api': str(match_data.get('id')),
                'home_team': home_team,
                'away_team': away_team,
                'match_date': match_data.get('utcDate'),
                'league': league_name,
                'status': connector.map_match_status(match_data.get('status')),
                'home_score': full_time.get('home'),
                'away_score': full_time.get('away'),
                'created_at': datetime.now().isoformat()
            }
            
            # Vérifier si le match existe déjà
            existing = self.supabase.table('matches').select('id').eq('match_id_api', data['match_id_api']).execute()
            
            if existing.data and len(existing.data) > 0:
                # Mise à jour du match existant (ex: scores en direct)
                result = self.supabase.table('matches').update(data).eq('match_id_api', data['match_id_api']).execute()
                print(f"✅ Match mis à jour: {home_team} vs {away_team}")
            else:
                # Insertion d'un nouveau match
                result = self.supabase.table('matches').insert(data).execute()
                print(f"✅ Match ajouté: {home_team} vs {away_team}")
            
            return result.data
        except Exception as e:
            print(f"❌ Erreur Supabase (football-data): {e}")
            return None
    
    def _map_status(self, status_short):
        """
        Mappe le statut API vers notre format (pour API-Football)
        """
        status_map = {
            'NS': 'scheduled',
            '1H': 'live',
            '2H': 'live',
            'HT': 'live',
            'ET': 'live',
            'P': 'live',
            'FT': 'finished',
            'AET': 'finished',
            'PEN': 'finished',
            'CANC': 'cancelled',
            'PST': 'postponed',
            'TBD': 'scheduled'
        }
        return status_map.get(status_short, 'scheduled')
    
    def get_matches_by_period(self, days_ahead=3):
        """
        Récupère les matchs des prochains jours
        """
        try:
            if not self.supabase:
                return []
            
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)
            
            result = self.supabase.table('matches').select('*').gte('match_date', today.isoformat()).lte('match_date', end_date.isoformat()).execute()
            return result.data
        except Exception as e:
            print(f"❌ Erreur récupération matchs: {e}")
            return []
    
    def get_live_matches(self):
        """
        Récupère les matchs en cours
        """
        try:
            if not self.supabase:
                return []
            
            result = self.supabase.table('matches').select('*').eq('status', 'live').execute()
            return result.data
        except Exception as e:
            print(f"❌ Erreur récupération live: {e}")
            return []
    
    def get_all_matches(self, limit=100):
        """
        Récupère tous les matchs (avec limite)
        """
        try:
            if not self.supabase:
                return []
            
            result = self.supabase.table('matches').select('*').order('match_date', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"❌ Erreur récupération tous matchs: {e}")
            return []
    
    def get_match_by_id(self, match_id_api):
        """
        Récupère un match spécifique par son ID API
        """
        try:
            if not self.supabase:
                return None
            
            result = self.supabase.table('matches').select('*').eq('match_id_api', str(match_id_api)).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ Erreur récupération match: {e}")
            return None
    
    def count_matches(self):
        """
        Compte le nombre total de matchs en base
        """
        try:
            if not self.supabase:
                return 0
            
            result = self.supabase.table('matches').select('*', count='exact').execute()
            return result.count if hasattr(result, 'count') else len(result.data)
        except Exception as e:
            print(f"❌ Erreur comptage matchs: {e}")
            return 0


# ============================================
# TEST RAPIDE (si exécuté directement)
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DU MATCH SERVICE")
    print("=" * 60)
    
    service = MatchService()
    
    # Test 1: Connexion
    print("\n📡 Test 1: Connexion Supabase")
    if service.supabase:
        print("   ✅ Supabase connecté")
    else:
        print("   ❌ Supabase non connecté")
    
    # Test 2: Compter les matchs
    print("\n📊 Test 2: Nombre de matchs en base")
    count = service.count_matches()
    print(f"   ✅ {count} matchs en base de données")
    
    # Test 3: Récupérer les derniers matchs
    print("\n⚽ Test 3: 5 derniers matchs")
    matches = service.get_all_matches(limit=5)
    if matches:
        for m in matches:
            home = m.get('home_team', '?')
            away = m.get('away_team', '?')
            date = m.get('match_date', '?')[:10] if m.get('match_date') else '?'
            print(f"   • {home} vs {away} - {date}")
    else:
        print("   ℹ️  Aucun match en base")
    
    print("\n" + "=" * 60)
    print("✅ FIN DU TEST MATCH SERVICE")
    print("=" * 60)