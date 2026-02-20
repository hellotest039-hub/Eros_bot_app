#!/usr/bin/env python3
"""🔮 Eros Bot - Time Series Agent (IA #3)"""

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


class TimeSeriesAgent(BasePredictionAgent):
    """
    IA #3 - Time Series Analyst
    
    Analyse:
    • Évolution des performances dans le temps
    • Séries en cours (invincibilité, sans victoire...)
    • Tendances saisonnières
    • Momentum récent (5 derniers matchs)
    """
    
    def __init__(self, weight: float = 0.9):
        super().__init__(name="time_series", weight=weight)
        self.lookback_matches = 5
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les tendances temporelles du match."""
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        
        # Simuler les séries temporelles (mocké - à connecter avec Supabase)
        home_trend = self._calculate_trend(home, is_home=True)
        away_trend = self._calculate_trend(away, is_home=False)
        
        # Analyser le momentum
        home_momentum = self._get_momentum(home)
        away_momentum = self._get_momentum(away)
        
        # Prédire Over/Under 2.5
        over_under_pred = self._predict_over_under(home_trend, away_trend)
        
        # Prédire BTTS (Both Teams To Score)
        btts_pred = self._predict_btts(home_momentum, away_momentum)
        
        # Prédiction 1N2 basée sur les tendances
        trend_diff = home_trend - away_trend
        if trend_diff > 0.2:
            prediction_1n2 = 'HOME_WIN'
            confidence_1n2 = min(0.85, 0.50 + trend_diff * 0.4)
        elif trend_diff < -0.2:
            prediction_1n2 = 'AWAY_WIN'
            confidence_1n2 = min(0.85, 0.50 + abs(trend_diff) * 0.4)
        else:
            prediction_1n2 = 'DRAW'
            confidence_1n2 = 0.45
        
        # Retourner TOUTES les prédictions de marchés
        return {
            'prediction': prediction_1n2,
            'confidence': round(confidence_1n2, 4),
            'reasoning': f"Tendance: {home} ({home_trend:.2f}) vs {away} ({away_trend:.2f}). Momentum: {home_momentum} vs {away_momentum}.",
            'markets': {
                '1N2': {
                    'prediction': prediction_1n2,
                    'confidence': round(confidence_1n2, 4)
                },
                'OVER_UNDER_2.5': {
                    'prediction': over_under_pred['prediction'],
                    'confidence': round(over_under_pred['confidence'], 4)
                },
                'BTTS': {
                    'prediction': btts_pred['prediction'],
                    'confidence': round(btts_pred['confidence'], 4)
                },
                'DOUBLE_CHANCE': {
                    'prediction': self._get_double_chance(prediction_1n2),
                    'confidence': round(min(0.95, confidence_1n2 + 0.20), 4)
                }
            },
            'details': {
                'home_trend': round(home_trend, 3),
                'away_trend': round(away_trend, 3),
                'home_momentum': home_momentum,
                'away_momentum': away_momentum,
                'model': 'Time Series Trend Analysis'
            }
        }
    
    def _calculate_trend(self, team_name: str, is_home: bool) -> float:
        """Calcule la tendance de performance (0.0 à 1.0)."""
        name_hash = sum(ord(c) for c in team_name.lower())
        base_trend = 0.5 + ((name_hash % 40) - 20) / 100
        
        # Bonus domicile
        if is_home:
            base_trend += 0.08
        
        return max(0.2, min(0.9, base_trend))
    
    def _get_momentum(self, team_name: str) -> str:
        """Retourne le momentum actuel (Positive, Neutral, Negative)."""
        name_hash = sum(ord(c) for c in team_name.lower())
        seed = name_hash % 10
        
        if seed < 4:
            return "Positive"
        elif seed < 7:
            return "Neutral"
        else:
            return "Negative"
    
    def _predict_over_under(self, home_trend: float, away_trend: float) -> Dict[str, Any]:
        """Prédit Over/Under 2.5 buts."""
        avg_trend = (home_trend + away_trend) / 2
        
        # Plus la tendance est haute, plus de buts attendus
        if avg_trend > 0.65:
            prediction = 'OVER_2.5'
            confidence = 0.50 + (avg_trend - 0.65) * 0.5
        elif avg_trend < 0.45:
            prediction = 'UNDER_2.5'
            confidence = 0.50 + (0.45 - avg_trend) * 0.5
        else:
            prediction = 'OVER_2.5'
            confidence = 0.45
        
        return {
            'prediction': prediction,
            'confidence': min(0.85, max(0.35, confidence))
        }
    
    def _predict_btts(self, home_momentum: str, away_momentum: str) -> Dict[str, Any]:
        """Prédit BTTS (Both Teams To Score)."""
        momentum_score = {'Positive': 0.7, 'Neutral': 0.5, 'Negative': 0.3}
        
        home_score = momentum_score.get(home_momentum, 0.5)
        away_score = momentum_score.get(away_momentum, 0.5)
        
        avg_score = (home_score + away_score) / 2
        
        if avg_score > 0.55:
            prediction = 'YES'
            confidence = 0.50 + (avg_score - 0.55) * 0.4
        else:
            prediction = 'NO'
            confidence = 0.50 + (0.55 - avg_score) * 0.4
        
        return {
            'prediction': f'BTTS_{prediction}',
            'confidence': min(0.80, max(0.40, confidence))
        }
    
    def _get_double_chance(self, prediction_1n2: str) -> str:
        """Retourne la double chance la plus sûre."""
        double_chance_map = {
            'HOME_WIN': '1N',
            'AWAY_WIN': 'N2',
            'DRAW': '12'
        }
        return double_chance_map.get(prediction_1n2, '1N')


if __name__ == "__main__":
    print("=" * 60)
    print("🔮 EROS BOT - TEST TIME SERIES AGENT")
    print("=" * 60)
    
    agent = TimeSeriesAgent(weight=0.9)
    print(f"✅ Agent: {agent.name}")
    
    test = {
        'home_team': 'PSG',
        'away_team': 'Lyon',
        'league': 'Ligue 1'
    }
    
    result = agent.predict(test)
    print(f"\n🏆 1N2: {result['markets']['1N2']['prediction']} ({result['markets']['1N2']['confidence']*100:.0f}%)")
    print(f"⚽ Over/Under: {result['markets']['OVER_UNDER_2.5']['prediction']} ({result['markets']['OVER_UNDER_2.5']['confidence']*100:.0f}%)")
    print(f"✅ BTTS: {result['markets']['BTTS']['prediction']} ({result['markets']['BTTS']['confidence']*100:.0f}%)")
    print(f"🛡️ Double Chance: {result['markets']['DOUBLE_CHANCE']['prediction']} ({result['markets']['DOUBLE_CHANCE']['confidence']*100:.0f}%)")
    print(f"💭 {result['reasoning']}")
    print("\n✅ SUCCÈS !" if result['prediction'] != 'ERROR' else "❌ ÉCHEC")
    print("=" * 60)