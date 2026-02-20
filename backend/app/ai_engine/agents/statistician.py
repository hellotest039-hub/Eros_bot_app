#!/usr/bin/env python3
"""🧮 Eros Bot - Statistician Agent (IA #1) - VERSION AUTONOME"""

from typing import Dict, Any, Tuple
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasePredictionAgent:
    """Classe de base simplifiée pour les agents IA."""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = max(0.0, min(1.0, weight))
        self.total_predictions = 0
        
    def predict(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode publique qui appelle _analyze."""
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
        """À implémenter par les classes filles."""
        raise NotImplementedError


class StatisticianAgent(BasePredictionAgent):
    """Agent IA basé sur l'analyse statistique."""
    
    def __init__(self, weight: float = 1.2):
        super().__init__(name="statistician", weight=weight)
        self.home_advantage = 1.15
        self.league_avg_goals = 1.4
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse statistique du match."""
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        
        # Calcul simplifié des forces
        home_hash = sum(ord(c) for c in home.lower())
        away_hash = sum(ord(c) for c in away.lower())
        
        home_attack = 0.9 + (home_hash % 40) / 100
        away_attack = 0.9 + (away_hash % 40) / 100
        home_defense = 0.9 + ((home_hash // 2) % 40) / 100
        away_defense = 0.9 + ((away_hash // 2) % 40) / 100
        
        # Expected Goals
        home_xg = self.league_avg_goals * home_attack * away_defense * self.home_advantage
        away_xg = self.league_avg_goals * away_attack * home_defense
        
        home_xg = max(0.3, min(3.0, home_xg))
        away_xg = max(0.3, min(3.0, away_xg))
        
        # Probabilités
        total_xg = home_xg + away_xg
        if total_xg > 0:
            base_home = home_xg / total_xg
            base_away = away_xg / total_xg
        else:
            base_home = base_away = 0.33
        
        p_draw = 0.25
        p_home = base_home * (1 - p_draw)
        p_away = base_away * (1 - p_draw)
        
        total = p_home + p_draw + p_away
        probs = {
            'HOME_WIN': round(p_home / total, 4),
            'DRAW': round(p_draw / total, 4),
            'AWAY_WIN': round(p_away / total, 4)
        }
        
        prediction = max(probs, key=probs.get)
        confidence = min(0.95, max(0.20, probs[prediction]))
        
        # Ajustement confiance
        sorted_p = sorted(probs.values(), reverse=True)
        if len(sorted_p) >= 2 and sorted_p[0] - sorted_p[1] < 0.10:
            confidence *= 0.85
        
        # Raisonnement
        diff = abs(home_xg - away_xg)
        if diff < 0.3:
            balance = "équilibré"
        elif diff < 0.7:
            balance = "légèrement favorable"
        else:
            balance = "favorable"
        
        stronger = home if home_xg > away_xg else away
        pred_fr = {'HOME_WIN': f'victoire {home}', 'DRAW': 'match nul', 'AWAY_WIN': f'victoire {away}'}.get(prediction, prediction)
        
        reasoning = f"xG: {home_xg:.2f} vs {away_xg:.2f} → Match {balance} → {pred_fr} ({confidence*100:.0f}%)"
        
        return {
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'reasoning': reasoning,
            'details': {
                'expected_goals': {'home': round(home_xg, 2), 'away': round(away_xg, 2)},
                'probabilities': probs,
                'model': 'Simplified Stats'
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🧮 EROS BOT - TEST STATISTICIEN")
    print("=" * 60)
    
    agent = StatisticianAgent(weight=1.2)
    print(f"✅ Agent: {agent.name}")
    
    test = {
        'home_team': 'PSG',
        'away_team': 'Lyon',
        'league': 'Ligue 1'
    }
    
    result = agent.predict(test)
    print(f"🏆 {result['prediction']} | 🎯 {result['confidence']*100:.1f}%")
    print(f"💭 {result['reasoning']}")
    print("✅ SUCCÈS !" if result['prediction'] != 'ERROR' else "❌ ÉCHEC")
    print("=" * 60)
