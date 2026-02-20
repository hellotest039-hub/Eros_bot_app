#!/usr/bin/env python3
"""📊 Eros Bot - Performance Tracker (Auto-Training)"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
import json

# Fix import Acode
sys.path.insert(0, '/sdcard/Eros_bot_app')

try:
    from dotenv import load_dotenv
    for env_path in [Path('/sdcard/Eros_bot_app/backend/.env'), Path('/sdcard/Eros_bot_app/.env')]:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            break
except ImportError:
    pass

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class PerformanceTracker:
    """
    Suit les performances des IA et calcule leurs précisions.
    
    Usage:
        tracker = PerformanceTracker()
        tracker.log_prediction(match_id, agent_name, prediction, confidence)
        tracker.log_result(match_id, actual_outcome)
        weights = tracker.get_optimal_weights()
    """
    
    def __init__(self):
        self.supabase = None
        if SUPABASE_AVAILABLE:
            try:
                supa_url = os.getenv("SUPABASE_URL")
                supa_key = os.getenv("SUPABASE_KEY")
                if supa_url and supa_key:
                    self.supabase = create_client(supa_url, supa_key)
            except:
                pass
        
        # Poids par défaut des IA
        self.default_weights = {
            'statistician': 1.2,
            'form_detector': 1.0,
            'time_series': 0.9,
            'context_analyst': 0.8
        }
        
        # Paramètres d'apprentissage
        self.learning_rate = 0.05  # Vitesse d'ajustement des poids
        self.min_weight = 0.5
        self.max_weight = 2.0
        self.min_predictions = 10  # Nombre min de prédictions pour ajuster
    
    def log_prediction(self, match_id: str, agent_name: str, 
                      predicted_outcome: str, confidence: float,
                      market_type: str = '1N2') -> bool:
        """Enregistre une prédiction pour suivi futur."""
        if not self.supabase:
            return False
        
        try:
            data = {
                'match_id': match_id,
                'agent_name': agent_name,
                'market_type': market_type,
                'predicted_outcome': predicted_outcome,
                'confidence': confidence,
                'predicted_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            self.supabase.table('prediction_logs').insert(data).execute()
            return True
        except Exception as e:
            print(f"⚠️ Erreur log_prediction: {e}")
            return False
    
    def log_result(self, match_id: str, actual_outcome: str,
                  home_score: int, away_score: int) -> bool:
        """Enregistre le résultat réel d'un match."""
        if not self.supabase:
            return False
        
        try:
            # Déterminer le résultat 1N2
            if home_score > away_score:
                result_1n2 = 'HOME_WIN'
            elif home_score < away_score:
                result_1n2 = 'AWAY_WIN'
            else:
                result_1n2 = 'DRAW'
            
            data = {
                'match_id': match_id,
                'actual_outcome_1n2': result_1n2,
                'home_score': home_score,
                'away_score': away_score,
                'total_goals': home_score + away_score,
                'resolved_at': datetime.now().isoformat()
            }
            
            # Mettre à jour ou insérer
            self.supabase.table('match_results').upsert(data, on_conflict='match_id').execute()
            
            # Mettre à jour le statut des prédictions
            self._update_prediction_statuses(match_id, result_1n2)
            
            return True
        except Exception as e:
            print(f"⚠️ Erreur log_result: {e}")
            return False
    
    def _update_prediction_statuses(self, match_id: str, actual_outcome: str):
        """Met à jour le statut des prédictions pour ce match."""
        if not self.supabase:
            return
        
        try:
            # Récupérer les prédictions en attente
            preds = self.supabase.table('prediction_logs').select('*').eq('match_id', match_id).eq('status', 'pending').execute()
            
            for pred in preds.data:
                is_correct = pred['predicted_outcome'] == actual_outcome
                
                self.supabase.table('prediction_logs').update({
                    'status': 'resolved',
                    'is_correct': is_correct,
                    'actual_outcome': actual_outcome,
                    'resolved_at': datetime.now().isoformat()
                }).eq('id', pred['id']).execute()
        except:
            pass
    
    def get_agent_accuracy(self, agent_name: str, days: int = 30, 
                          market_type: str = '1N2') -> Dict[str, float]:
        """Calcule la précision d'une IA sur les N derniers jours."""
        if not self.supabase:
            return {'accuracy': 0.5, 'count': 0, 'avg_confidence': 0.5}
        
        try:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.supabase.table('prediction_logs').select('*').eq('agent_name', agent_name).eq('market_type', market_type).eq('status', 'resolved').gte('predicted_at', since).execute()
            
            logs = result.data if hasattr(result, 'data') else []
            
            if not logs:
                return {'accuracy': 0.5, 'count': 0, 'avg_confidence': 0.5}
            
            correct = sum(1 for l in logs if l.get('is_correct', False))
            total = len(logs)
            avg_conf = sum(l.get('confidence', 0.5) for l in logs) / total
            
            return {
                'accuracy': correct / total if total > 0 else 0.5,
                'count': total,
                'avg_confidence': avg_conf,
                'correct': correct,
                'total': total
            }
        except Exception as e:
            print(f"⚠️ Erreur get_agent_accuracy: {e}")
            return {'accuracy': 0.5, 'count': 0, 'avg_confidence': 0.5}
    
    def get_optimal_weights(self) -> Dict[str, float]:
        """Calcule les poids optimaux basés sur les performances récentes."""
        weights = {}
        
        for agent_name in self.default_weights.keys():
            stats = self.get_agent_accuracy(agent_name)
            
            if stats['count'] >= self.min_predictions:
                # Ajustement basé sur la précision vs confiance moyenne
                calibration = stats['accuracy'] / stats['avg_confidence'] if stats['avg_confidence'] > 0 else 1.0
                
                # Nouveau poids = poids par défaut × facteur de calibration
                new_weight = self.default_weights[agent_name] * (0.7 + 0.6 * calibration)
                
                # Clamp dans les limites
                weights[agent_name] = max(self.min_weight, min(self.max_weight, new_weight))
            else:
                # Pas assez de données → poids par défaut
                weights[agent_name] = self.default_weights[agent_name]
        
        # Normaliser pour que la somme soit ~4.0 (moyenne 1.0 par IA)
        total = sum(weights.values())
        if total > 0:
            factor = 4.0 / total
            weights = {k: round(v * factor, 3) for k, v in weights.items()}
        
        return weights
    
    def save_weights(self, weights: Dict[str, float]) -> bool:
        """Sauvegarde les poids dans Supabase."""
        if not self.supabase:
            return False
        
        try:
            data = {
                'weights': json.dumps(weights),
                'updated_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            self.supabase.table('ai_weights').upsert(data, on_conflict='id').execute()
            return True
        except:
            return False
    
    def load_weights(self) -> Dict[str, float]:
        """Charge les poids depuis Supabase."""
        if not self.supabase:
            return self.default_weights.copy()
        
        try:
            result = self.supabase.table('ai_weights').select('*').limit(1).execute()
            if result.data and len(result.data) > 0:
                return json.loads(result.data[0].get('weights', '{}'))
        except:
            pass
        
        return self.default_weights.copy()
    
    def train_step(self) -> Dict[str, Any]:
        """Exécute une étape d'entraînement et retourne les résultats."""
        print("🔄 Lancement de l'auto-training...")
        
        # Calculer les nouveaux poids
        new_weights = self.get_optimal_weights()
        
        # Charger les poids actuels
        current_weights = self.load_weights()
        
        # Calculer les changements
        changes = {}
        for agent in new_weights:
            old_w = current_weights.get(agent, self.default_weights[agent])
            new_w = new_weights[agent]
            changes[agent] = {
                'old': round(old_w, 3),
                'new': round(new_w, 3),
                'delta': round(new_w - old_w, 3)
            }
        
        # Sauvegarder si changement significatif
        max_change = max(abs(c['delta']) for c in changes.values())
        if max_change >= 0.1:
            self.save_weights(new_weights)
            print("✅ Nouveaux poids sauvegardés")
        
        # Résumé
        summary = {
            'weights': new_weights,
            'changes': changes,
            'max_change': round(max_change, 3),
            'saved': max_change >= 0.1
        }
        
        print(f"📊 Auto-training terminé (changement max: {max_change:.3f})")
        return summary


# ============================================
# 🧪 TEST
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("📊 EROS BOT - TEST PERFORMANCE TRACKER")
    print("=" * 60)
    
    tracker = PerformanceTracker()
    print(f"✅ Tracker initialisé")
    print(f"📈 Poids par défaut: {tracker.default_weights}")
    
    # Test: Get accuracy (mocked si pas de données)
    print("\n📊 Précisions récentes (30 jours):")
    for agent in tracker.default_weights.keys():
        stats = tracker.get_agent_accuracy(agent)
        icon = "✅" if stats['count'] >= 10 else "⚠️"
        print(f"   {icon} {agent}: {stats['accuracy']*100:.1f}% ({stats['count']} prédictions)")
    
    # Test: Get optimal weights
    print("\n⚖️ Poids optimaux calculés:")
    weights = tracker.get_optimal_weights()
    for agent, weight in weights.items():
        default = tracker.default_weights[agent]
        change = "↑" if weight > default else ("↓" if weight < default else "→")
        print(f"   {agent}: {weight:.3f} {change} (défaut: {default:.3f})")
    
    # Test: Train step
    print("\n🔄 Exécution d'un train step:")
    result = tracker.train_step()
    
    if result['changes']:
        print("\n📈 Changements de poids:")
        for agent, change in result['changes'].items():
            arrow = "↑" if change['delta'] > 0 else ("↓" if change['delta'] < 0 else "→")
            print(f"   {agent}: {change['old']:.3f} → {change['new']:.3f} {arrow}{abs(change['delta']):.3f}")
    
    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")
    print("=" * 60)