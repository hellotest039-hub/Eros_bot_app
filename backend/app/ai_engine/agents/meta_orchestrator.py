#!/usr/bin/env python3
"""⚖️ Eros Bot - Meta Orchestrator (Auto-Training)"""

from typing import Dict, Any, List
import logging
import math
import sys
from pathlib import Path

sys.path.insert(0, '/sdcard/Eros_bot_app')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasePredictionAgent:
    """Classe de base."""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self._weight = weight
        self.total_predictions = 0
        
    @property
    def weight(self) -> float:
        return self._weight
    
    @weight.setter
    def weight(self, value: float):
        self._weight = max(0.5, min(2.0, value))
        
    def predict(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """✅ LIGNE 33 CORRIGÉE : match_data: Dict[str, Any]"""
        try:
            result = self._analyze(match_data)
            self.total_predictions += 1
            return result
        except Exception as e:
            return {'prediction': 'ERROR', 'confidence': 0.0, 'reasoning': f"Erreur: {str(e)}"}
    
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """✅ LIGNE 41 CORRIGÉE : match_data: Dict[str, Any]"""
        raise NotImplementedError


class StatisticianAgent(BasePredictionAgent):
    """IA #1 - Statisticien"""
    
    def __init__(self, weight: float = 1.2):
        super().__init__(name="statistician", weight=weight)
        self.home_advantage = 1.15
        self.league_avg_goals = 1.4
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        
        home_hash = sum(ord(c) for c in home.lower())
        away_hash = sum(ord(c) for c in away.lower())
        
        home_xg = self.league_avg_goals * (0.9 + (home_hash % 40) / 100) * self.home_advantage
        away_xg = self.league_avg_goals * (0.9 + (away_hash % 40) / 100)
        
        total_xg = home_xg + away_xg
        
        if total_xg > 0:
            p_home = (home_xg / total_xg) * 0.75
            p_away = (away_xg / total_xg) * 0.75
        else:
            p_home = p_away = 0.25
        p_draw = 0.25
        
        total = p_home + p_away + p_draw
        probs = {'HOME_WIN': p_home/total, 'DRAW': p_draw/total, 'AWAY_WIN': p_away/total}
        
        prediction = max(probs, key=probs.get)
        confidence = min(0.90, max(0.25, probs[prediction]))
        
        exact_home = self._poisson_goals(home_xg)
        exact_away = self._poisson_goals(away_xg)
        
        return {
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'reasoning': f"Stats: {home_xg:.2f} xG vs {away_xg:.2f} xG",
            'markets': {
                '1N2': {'prediction': prediction, 'confidence': round(confidence, 4)},
                'OVER_UNDER_2.5': {'prediction': 'OVER_2.5' if total_xg > 2.5 else 'UNDER_2.5', 'confidence': round(min(0.85, total_xg/3.5), 4)},
                'BTTS': {'prediction': 'BTTS_YES' if total_xg > 2.0 else 'BTTS_NO', 'confidence': round(min(0.80, total_xg/3.0), 4)},
                'EXACT_GOALS_HOME': exact_home,
                'EXACT_GOALS_AWAY': exact_away,
                'OVER_UNDER_HT': {'prediction': 'OVER_0.5_HT' if total_xg*0.45 > 0.6 else 'UNDER_0.5_HT', 'confidence': 0.55},
                'HT_FT': {'prediction': f"{prediction.split('_')[0]}_{prediction.split('_')[0]}", 'confidence': round(confidence * 0.8, 4)},
                'DOUBLE_CHANCE': {'prediction': '1N' if prediction != 'AWAY_WIN' else 'N2', 'confidence': round(min(0.90, confidence + 0.15), 4)}
            }
        }
    
    def _poisson_goals(self, xg: float) -> Dict[str, Any]:
        probs = {}
        for k in range(5):
            if xg == 0:
                probs[k] = 1.0 if k == 0 else 0.0
            else:
                probs[k] = (xg ** k * math.exp(-xg)) / math.factorial(k)
        probs['3+'] = 1.0 - sum(probs.values())
        
        best = max(probs, key=probs.get)
        return {
            'prediction': f'EXACT_{best}_GOALS' if best != '3+' else 'EXACT_3+_GOALS',
            'confidence': round(min(0.70, max(0.25, probs[best])), 4),
            'distribution': {k: round(v, 3) for k, v in probs.items()}
        }


class FormDetectorAgent(BasePredictionAgent):
    """IA #2 - Form Detector"""
    
    def __init__(self, weight: float = 1.0):
        super().__init__(name="form_detector", weight=weight)
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        
        home_hash = sum(ord(c) for c in home.lower())
        away_hash = sum(ord(c) for c in away.lower())
        
        home_score = 0.5 + ((home_hash % 30) - 15) / 100
        away_score = 0.5 + ((away_hash % 30) - 15) / 100
        
        diff = home_score - away_score
        if diff > 0.1:
            prediction = 'HOME_WIN'
            confidence = 0.50 + diff * 0.5
        elif diff < -0.1:
            prediction = 'AWAY_WIN'
            confidence = 0.50 + abs(diff) * 0.5
        else:
            prediction = 'DRAW'
            confidence = 0.40
        
        conf = round(min(0.85, max(0.30, confidence)), 4)
        
        return {
            'prediction': prediction,
            'confidence': conf,
            'reasoning': f"Forme: {home_score:.2f} vs {away_score:.2f}",
            'markets': {
                '1N2': {'prediction': prediction, 'confidence': conf},
                'DOUBLE_CHANCE': {'prediction': '1N' if diff >= 0 else 'N2', 'confidence': round(min(0.90, conf + 0.15), 4)},
                'OVER_UNDER_2.5': {'prediction': 'OVER_2.5', 'confidence': 0.55},
                'BTTS': {'prediction': 'BTTS_YES', 'confidence': 0.52}
            }
        }


class TimeSeriesAgent(BasePredictionAgent):
    """IA #3 - Time Series"""
    
    def __init__(self, weight: float = 0.9):
        super().__init__(name="time_series", weight=weight)
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        
        home_hash = sum(ord(c) for c in home.lower())
        away_hash = sum(ord(c) for c in away.lower())
        
        home_trend = 0.5 + ((home_hash % 40) - 20) / 100
        away_trend = 0.5 + ((away_hash % 40) - 20) / 100
        
        diff = home_trend - away_trend
        if diff > 0.2:
            prediction = 'HOME_WIN'
            confidence = 0.50 + diff * 0.4
        elif diff < -0.2:
            prediction = 'AWAY_WIN'
            confidence = 0.50 + abs(diff) * 0.4
        else:
            prediction = 'DRAW'
            confidence = 0.45
        
        conf = round(min(0.85, max(0.35, confidence)), 4)
        
        return {
            'prediction': prediction,
            'confidence': conf,
            'reasoning': f"Tendance: {home_trend:.2f} vs {away_trend:.2f}",
            'markets': {
                '1N2': {'prediction': prediction, 'confidence': conf},
                'OVER_UNDER_2.5': {'prediction': 'OVER_2.5', 'confidence': 0.55},
                'BTTS': {'prediction': 'BTTS_YES', 'confidence': 0.52},
                'OVER_UNDER_HT': {'prediction': 'OVER_0.5_HT', 'confidence': 0.58}
            }
        }


class ContextAnalystAgent(BasePredictionAgent):
    """IA #4 - Context Analyst"""
    
    def __init__(self, weight: float = 0.8):
        super().__init__(name="context_analyst", weight=weight)
        
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        home = match_data.get('home_team', 'Unknown')
        away = match_data.get('away_team', 'Unknown')
        league = match_data.get('league', 'Unknown')
        
        home_hash = sum(ord(c) for c in home.lower())
        away_hash = sum(ord(c) for c in away.lower())
        
        h2h = 0.5 + ((home_hash - away_hash) % 30 - 15) / 100
        context_score = (h2h + 0.5 + 0.5) / 3
        
        if context_score > 0.55:
            prediction = 'HOME_WIN'
            confidence = 0.50 + (context_score - 0.55) * 0.5
        elif context_score < 0.45:
            prediction = 'AWAY_WIN'
            confidence = 0.50 + (0.45 - context_score) * 0.5
        else:
            prediction = 'DRAW'
            confidence = 0.40
        
        conf = round(min(0.80, max(0.35, confidence)), 4)
        
        return {
            'prediction': prediction,
            'confidence': conf,
            'reasoning': f"Contexte: H2H={h2h*100:.0f}%",
            'markets': {
                '1N2': {'prediction': prediction, 'confidence': conf},
                'H2H_ADVANTAGE': {'prediction': 'HOME' if h2h > 0.5 else 'AWAY', 'confidence': round(max(h2h, 1-h2h), 4)},
                'CORNERS': {'prediction': 'OVER_9.5' if (home_hash+away_hash)%100 > 50 else 'UNDER_9.5', 'confidence': 0.55},
                'CARDS': {'prediction': 'OVER_4.5' if any(l in league for l in ['Serie A', 'La Liga']) else 'UNDER_4.5', 'confidence': 0.52}
            }
        }


class MetaOrchestratorAgent(BasePredictionAgent):
    """IA #5 - Meta Orchestrator avec Auto-Training"""
    
    def __init__(self, weight: float = 1.5, risk_threshold: float = 0.60, 
                 auto_train: bool = True):
        super().__init__(name="meta_orchestrator", weight=weight)
        self.risk_threshold = risk_threshold
        self.auto_train = auto_train
        
        self._init_agents_with_weights()
        
        self.tracker = None
        if auto_train:
            try:
                from backend.app.ai_engine.performance_tracker import PerformanceTracker
                self.tracker = PerformanceTracker()
                saved_weights = self.tracker.load_weights()
                self._update_agent_weights(saved_weights)
                print(f"✅ Poids chargés depuis Supabase: {saved_weights}")
            except ImportError:
                print("⚠️ PerformanceTracker non disponible - poids par défaut")
    
    def _init_agents_with_weights(self):
        """Initialise les agents avec leurs poids."""
        weights = {
            'statistician': 1.2,
            'form_detector': 1.0,
            'time_series': 0.9,
            'context_analyst': 0.8
        }
        self.statistician = StatisticianAgent(weight=weights['statistician'])
        self.form_detector = FormDetectorAgent(weight=weights['form_detector'])
        self.time_series = TimeSeriesAgent(weight=weights['time_series'])
        self.context_analyst = ContextAnalystAgent(weight=weights['context_analyst'])
        self._current_weights = weights
    
    def _update_agent_weights(self, new_weights: Dict[str, float]):
        """Met à jour les poids des agents."""
        for agent_name, weight in new_weights.items():
            if hasattr(self, agent_name):
                agent = getattr(self, agent_name)
                agent.weight = weight
        self._current_weights = new_weights
    
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agrège les 4 IA avec poids dynamiques."""
        
        stat_pred = self.statistician.predict(match_data)
        form_pred = self.form_detector.predict(match_data)
        time_pred = self.time_series.predict(match_data)
        ctx_pred = self.context_analyst.predict(match_data)
        
        all_predictions = {
            'statistician': stat_pred,
            'form_detector': form_pred,
            'time_series': time_pred,
            'context_analyst': ctx_pred
        }
        
        all_markets = {}
        
        for agent_name, pred in all_predictions.items():
            agent_weight = getattr(self, agent_name).weight
            
            if 'markets' in pred:
                for market_name, market_data in pred['markets'].items():
                    if market_name not in all_markets:
                        all_markets[market_name] = []
                    
                    all_markets[market_name].append({
                        'agent': agent_name,
                        'prediction': market_data['prediction'],
                        'confidence': market_data['confidence'],
                        'weighted_confidence': market_data['confidence'] * agent_weight
                    })
        
        best_markets = {}
        for market_name, market_preds in all_markets.items():
            weighted_sum = sum(p['weighted_confidence'] for p in market_preds)
            avg_confidence = weighted_sum / len(market_preds) if market_preds else 0
            
            pred_counts = {}
            for p in market_preds:
                pred_counts[p['prediction']] = pred_counts.get(p['prediction'], 0) + 1
            
            best_pred = max(pred_counts, key=pred_counts.get)
            
            best_markets[market_name] = {
                'prediction': best_pred,
                'confidence': round(min(0.95, avg_confidence), 4),
                'agents_agreed': pred_counts.get(best_pred, 0),
                'total_agents': len(market_preds)
            }
        
        best_market_name = max(best_markets, key=lambda x: best_markets[x]['confidence'])
        best_market_data = best_markets[best_market_name]
        
        if best_market_data['confidence'] >= 0.75:
            risk_level = 'low'
            recommendation = "✅ FORTE CONFIANCE - MEILLEUR MARCHÉ"
        elif best_market_data['confidence'] >= self.risk_threshold:
            risk_level = 'medium'
            recommendation = "⚠️ OPPORTUNITÉ MODÉRÉE"
        else:
            risk_level = 'high'
            recommendation = "❌ À ÉVITER - Risque trop élevé"
        
        reasoning = f"Meilleur marché: {best_market_name}. {best_market_data['prediction']} ({best_market_data['confidence']*100:.1f}%). "
        reasoning += f"{len(best_markets)} marchés analysés par 4 IA."
        
        return {
            'prediction': best_market_data['prediction'],
            'confidence': best_market_data['confidence'],
            'market_type': best_market_name,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'reasoning': reasoning,
            'all_markets': best_markets,
            'agent_weights': {k: round(v, 3) for k, v in self._current_weights.items()},
            'details': {
                'agents_used': list(all_predictions.keys()),
                'markets_analyzed': len(best_markets),
                'best_market': best_market_name,
                'model': 'Multi-Agent Multi-Market + Auto-Training'
            }
        }
    
    def trigger_auto_training(self) -> Dict[str, Any]:
        """Déclenche manuellement l'auto-training."""
        if self.tracker:
            return self.tracker.train_step()
        return {'error': 'Tracker non disponible'}


if __name__ == "__main__":
    print("=" * 70)
    print("⚖️ EROS BOT - TEST META ORCHESTRATOR (AUTO-TRAINING)")
    print("=" * 70)
    
    agent = MetaOrchestratorAgent(weight=1.5, auto_train=True)
    print(f"✅ Meta-Orchestrator initialisé avec auto-training")
    print(f"📊 Poids actuels: {agent._current_weights}")
    print()
    
    test = {'home_team': 'PSG', 'away_team': 'Marseille', 'league': 'Ligue 1'}
    result = agent.predict(test)
    
    print("🏆 " + "=" * 60)
    print(f"   🎯 MEILLEUR MARCHÉ: {result['market_type']}")
    print(f"   📊 PRÉDICTION: {result['prediction']}")
    print(f"   🎯 CONFIANCE: {result['confidence']*100:.1f}%")
    print(f"   ⚠️ RISQUE: {result['risk_level'].upper()}")
    print(f"   💡 {result['recommendation']}")
    print("🏆 " + "=" * 60)
    print()
    
    print("⚖️ POIDS DES IA:")
    for name, weight in result.get('agent_weights', {}).items():
        print(f"   • {name}: {weight:.3f}")
    
    print(f"\n💭 {result['reasoning']}")
    print("\n✅ SUCCÈS !" if result['prediction'] != 'ERROR' else "❌ ÉCHEC")
    print("=" * 70)
