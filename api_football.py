import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class APIFootballConnector:
    def __init__(self):
        self.api_key = os.getenv("97d31ffacc6d7866a4982420dfce91368966910262788668d949ce685e462636")
        self.host = "api-football-v1.p.rapidapi.com"
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.host
        }
    
    def get_matches_by_date(self, date_str):
        """Récupère les matchs pour une date donnée (YYYY-MM-DD)"""
        url = f"{self.base_url}/fixtures"
        params = {'date': date_str}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except Exception as e:
            print(f"❌ Erreur API Football: {e}")
            return []
    
    def get_live_matches(self):
        """Récupère les matchs en cours"""
        url = f"{self.base_url}/fixtures"
        params = {'live': 'all'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except Exception as e:
            print(f"❌ Erreur API Football Live: {e}")
            return []
    
    def get_leagues(self):
        """Récupère la liste des championnats"""
        url = f"{self.base_url}/leagues"
        params = {'season': datetime.now().year}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except Exception as e:
            print(f"❌ Erreur API Football Leagues: {e}")
            return []