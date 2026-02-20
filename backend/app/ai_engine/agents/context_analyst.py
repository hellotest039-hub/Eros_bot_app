#!/usr/bin/env python3
"""🗣️ Eros Bot - Context Analyst Agent (IA #4)"""

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


class ContextAnalystAgent(BasePredictionAgent):
    """
    IA #4 - Context Analyst
    
    Analyse:
    • Historique des confrontations (H2H)
    • Performance domicile vs extérieur
    • Enjeux du match (titre, relégation, coupe...)
    • Facteurs externes (météo, terrain, arbitre...)
    """
    
    def __init__(self, weight: float = 0.8):
        super().__init__(name="context_analyst", weight=weight)
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le contexte du match."""
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        league = match_data.get('league', 'Unknown')
        
        # Analyser l'historique H2H (mocké)
        h2h_advantage = self._get_h2h_advantage(home, away)
        
        # Analyser performance domicile/extérieur
        home_perf = self._get_home_performance(home)
        away_perf = self._get_away_performance(away)
        
        # Analyser les enjeux
        stakes_factor = self._get_stakes_factor(league)
        
        # Prédiction basée sur le contexte
        context_score = (h2h_advantage + home_perf + away_perf + stakes_factor) / 4
        
        # Marché 1N2
        if context_score > 0.55:
            prediction_1n2 = 'HOME_WIN'
            confidence_1n2 = 0.50 + (context_score - 0.55) * 0.5
        elif context_score < 0.45:
            prediction_1n2 = 'AWAY_WIN'
            confidence_1n2 = 0.50 + (0.45 - context_score) * 0.5
        else:
            prediction_1n2 = 'DRAW'
            confidence_1n2 = 0.40
        
        # Marché Corner (mocké)
        corner_pred = self._predict_corners(home, away)
        
        # Marché Cartons (mocké)
        card_pred = self._predict_cards(league)
        
        # Meilleur marché selon le contexte
        best_market = self._find_best_market({
            '1N2': confidence_1n2,
            'H2H': h2h_advantage,
            'HOME_PERF': home_perf,
            'CORNER': corner_pred['confidence'],
            'CARD': card_pred['confidence']
        })
        
        return {
            'prediction': prediction_1n2,
            'confidence': round(confidence_1n2, 4),
            'reasoning': f"H2H: {h2h_advantage*100:.0f}% | Domicile: {home_perf*100:.0f}% | Extérieur: {away_perf*100:.0f}% | Enjeu: {stakes_factor*100:.0f}%",
            'markets': {
                '1N2': {
                    'prediction': prediction_1n2,
                    'confidence': round(confidence_1n2, 4)
                },
                'H2H_ADVANTAGE': {
                    'prediction': 'HOME' if h2h_advantage > 0.5 else 'AWAY',
                    'confidence': round(max(h2h_advantage, 1-h2h_advantage), 4)
                },
                'CORNERS': {
                    'prediction': corner_pred['prediction'],
                    'confidence': round(corner_pred['confidence'], 4)
                },
                'CARDS': {
                    'prediction': card_pred['prediction'],
                    'confidence': round(card_pred['confidence'], 4)
                }
            },
            'best_market': best_market,
            'details': {
                'h2h_advantage': round(h2h_advantage, 3),
                'home_performance': round(home_perf, 3),
                'away_performance': round(away_perf, 3),
                'stakes_factor': round(stakes_factor, 3),
                'model': 'Contextual Analysis + H2H'
            }
        }
    
    def _get_h2h_advantage(self, home: str, away: str) -> float:
        """Simule l'avantage historique entre les équipes."""
        home_hash = sum(ord(c) for c in home.lower())
        away_hash = sum(ord(c) for c in away.lower())
        
        # 0.5 = égalité, >0.5 = avantage domicile, <0.5 = avantage extérieur
        h2h = 0.5 + ((home_hash - away_hash) % 30 - 15) / 100
        return max(0.3, min(0.8, h2h))
    
    def _get_home_performance(self, team_name: str) -> float:
        """Performance à domicile de l'équipe."""
        name_hash = sum(ord(c) for c in team_name.lower())
        perf = 0.5 + (name_hash % 35 - 17) / 100
        return max(0.3, min(0.9, perf + 0.10))  # +10% bonus domicile
    
    def _get_away_performance(self, team_name: str) -> float:
        """Performance à l'extérieur de l'équipe."""
        name_hash = sum(ord(c) for c in team_name.lower())
        perf = 0.5 + (name_hash % 35 - 17) / 100
        return max(0.2, min(0.8, perf - 0.10))  # -10% malus extérieur
    
    def _get_stakes_factor(self, league: str) -> float:
        """Facteur d'enjeu selon le championnat."""
        high_stakes_leagues = ['Premier League', 'La Liga', 'Champions League', 'Ligue 1']
        if any(l in league for l in high_stakes_leagues):
            return 0.65  # Enjeux élevés
        return 0.50  # Enjeux normaux
    
    def _predict_corners(self, home: str, away: str) -> Dict[str, Any]:
        """Prédit le marché des corners."""
        home_hash = sum(ord(c) for c in home.lower())
        away_hash = sum(ord(c) for c in away.lower())
        
        avg_hash = (home_hash + away_hash) / 2
        if avg_hash % 100 > 50:
            prediction = 'OVER_9.5'
            confidence = 0.50 + ((avg_hash % 50) / 100)
        else:
            prediction = 'UNDER_9.5'
            confidence = 0.50 + ((50 - avg_hash % 50) / 100)
        
        return {
            'prediction': prediction,
            'confidence': min(0.80, max(0.40, confidence))
        }
    
    def _predict_cards(self, league: str) -> Dict[str, Any]:
        """Prédit le marché des cartons."""
        aggressive_leagues = ['Serie A', 'La Liga', 'Championship']
        
        if any(l in league for l in aggressive_leagues):
            prediction = 'OVER_4.5'
            confidence = 0.55
        else:
            prediction = 'UNDER_4.5'
            confidence = 0.50
        
        return {
            'prediction': prediction,
            'confidence': confidence
        }
    
    def _find_best_market(self, markets: Dict[str, float]) -> Dict[str, Any]:
        """Trouve le marché avec la plus forte confiance."""
        best = max(markets, key=markets.get)
        return {
            'name': best,
            'confidence': round(markets[best], 4)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🗣️ EROS BOT - TEST CONTEXT ANALYST")
    print("=" * 60)
    
    agent = ContextAnalystAgent(weight=0.8)
    print(f"✅ Agent: {agent.name}")
    
    test = {
        'home_team': 'PSG',
        'away_team': 'Marseille',
        'league': 'Ligue 1'
    }
    
    result = agent.predict(test)
    print(f"\n🏆 1N2: {result['markets']['1N2']['prediction']} ({result['markets']['1N2']['confidence']*100:.0f}%)")
    print(f"📊 H2H: {result['markets']['H2H_ADVANTAGE']['prediction']} ({result['markets']['H2H_ADVANTAGE']['confidence']*100:.0f}%)")
    print(f"🚩 Corners: {result['markets']['CORNERS']['prediction']} ({result['markets']['CORNERS']['confidence']*100:.0f}%)")
    print(f"🟨 Cartons: {result['markets']['CARDS']['prediction']} ({result['markets']['CARDS']['confidence']*100:.0f}%)")
    print(f"\n🎯 MEILLEUR MARCHÉ: {result['best_market']['name']} ({result['best_market']['confidence']*100:.0f}%)")
    print(f"💭 {result['reasoning']}")
    print("\n✅ SUCCÈS !" if result['prediction'] != 'ERROR' else "❌ ÉCHEC")
    print("=" * 60)
