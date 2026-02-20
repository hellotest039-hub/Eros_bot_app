#!/usr/bin/env python3
"""📈 Eros Bot - Form Detector Agent (IA #2) - VERSION AUTONOME"""

from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasePredictionAgent:
    """Classe de base simplifiée."""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = max(0.0, min(1.0, weight))
        self.total_predictions = 0
        
    def predict(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = self._analyze(match_data)
            self.total_predictions += 1
            return result
        except Exception as e:
            return {
                'prediction': 'ERROR',
                'confidence': 0.0,
                'reasoning': f"Erreur: {str(e)}"
            }
    
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class FormDetectorAgent(BasePredictionAgent):
    """IA basée sur l'analyse de la forme récente des équipes."""
    
    def __init__(self, weight: float = 1.0):
        super().__init__(name="form_detector", weight=weight)
        self.lookback_matches = 5
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la forme récente des équipes."""
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        
        home_form = self._get_recent_form(home, is_home=True)
        away_form = self._get_recent_form(away, is_home=False)
        
        home_score = self._calculate_form_score(home_form)
        away_score = self._calculate_form_score(away_form)
        
        diff = home_score - away_score
        if diff > 0.15:
            prediction = 'HOME_WIN'
            confidence = min(0.90, 0.50 + diff * 0.5)
        elif diff < -0.15:
            prediction = 'AWAY_WIN'
            confidence = min(0.90, 0.50 + abs(diff) * 0.5)
        else:
            prediction = 'DRAW'
            confidence = 0.40 + abs(diff) * 0.3
        
        home_wins = home_form.count('W')
        away_wins = away_form.count('W')
        home_str = ''.join(home_form)
        away_str = ''.join(away_form)
        
        if abs(diff) < 0.1:
            balance = "forme équivalente"
        elif abs(diff) < 0.25:
            balance = "légèrement meilleure"
        else:
            balance = "nettement meilleure"
        
        better = home if home_score > away_score else away
        reasoning = f"Forme: {home} ({home_str}={home_wins}V) vs {away} ({away_str}={away_wins}V). {better} a une forme {balance}."
        
        return {
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'reasoning': reasoning,
            'details': {
                'home_form': home_form,
                'away_form': away_form,
                'home_score': round(home_score, 3),
                'away_score': round(away_score, 3),
                'model': 'Recent Form Analysis'
            }
        }
    
    def _get_recent_form(self, team_name: str, is_home: bool) -> List[str]:
        """Simule les résultats récents d'une équipe."""
        name_hash = sum(ord(c) for c in team_name.lower())
        location_bonus = 1 if is_home else 0
        
        results = []
        for i in range(self.lookback_matches):
            seed = (name_hash + i * 7 + location_bonus * 3) % 10
            if seed < 4:
                results.append('W')
            elif seed < 7:
                results.append('D')
            else:
                results.append('L')
        
        return results
    
    def _calculate_form_score(self, results: List[str]) -> float:
        """Calcule un score de forme (0.0 à 1.0)."""
        if not results:
            return 0.5
        
        score = 0
        total_weight = 0
        
        for i, result in enumerate(reversed(results)):
            weight = 1.0 + (i * 0.15)
            
            if result == 'W':
                points = 3
            elif result == 'D':
                points = 1
            else:
                points = 0
            
            score += points * weight
            total_weight += 3 * weight
        
        return max(0.1, min(0.9, score / total_weight))


if __name__ == "__main__":
    print("=" * 60)
    print("📈 EROS BOT - TEST FORM DETECTOR")
    print("=" * 60)
    
    agent = FormDetectorAgent(weight=1.0)
    print(f"✅ Agent: {agent.name}")
    
    test = {
        'home_team': 'PSG',
        'away_team': 'Lyon',
        'league': 'Ligue 1'
    }
    
    result = agent.predict(test)
    print(f"🏆 {result['prediction']} | 🎯 {result['confidence']*100:.1f}%")
    print(f"💭 {result['reasoning']}")
    
    if 'details' in result:
        print(f"\n📊 Détails:")
        print(f"   Forme Domicile: {result['details']['home_form']} (score: {result['details']['home_score']})")
        print(f"   Forme Extérieur: {result['details']['away_form']} (score: {result['details']['away_score']})")
    
    print("✅ SUCCÈS !" if result['prediction'] != 'ERROR' else "❌ ÉCHEC")
    print("=" * 60)