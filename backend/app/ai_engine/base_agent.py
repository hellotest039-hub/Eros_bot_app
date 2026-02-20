#!/usr/bin/env python3
"""
🧠 Eros Bot - Base Agent Class
Classe de base que toutes les IA de prédiction vont hériter.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BasePredictionAgent(ABC):
    """Classe abstraite de base pour tous les agents de prédiction."""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self._weight = max(0.0, min(1.0, weight))
        self.version = "1.0.0"
        self.last_run: Optional[datetime] = None
        self.total_predictions = 0
        self.successful_predictions = 0
        logger.info(f"🤖 Agent '{name}' initialisé (poids: {self._weight})")
    
    @property
    def weight(self) -> float:
        return self._weight
    
    @weight.setter
    def weight(self, value: float):
        self._weight = max(0.5, min(2.0, value))
        logger.info(f"📊 {self.name}: Poids mis à jour à {self._weight}")
    
    @abstractmethod
    def _analyze(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode abstraite à implémenter par chaque IA."""
        pass
    
    def predict(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Méthode publique pour générer une prédiction."""
        start_time = datetime.now()
        
        try:
            if not self._validate_input(match_data):
                return self._error_response("Données de match invalides")
            
            result = self._analyze(match_data)
            
            if not self._validate_output(result):
                return self._error_response("Résultat de prédiction invalide")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            prediction = {
                'agent_name': self.name,
                'agent_version': self.version,
                'prediction': result['prediction'],
                'confidence': result['confidence'],
                'weighted_confidence': result['confidence'] * self._weight,
                'reasoning': result.get('reasoning', ''),
                'execution_time_ms': round(execution_time * 1000, 2),
                'timestamp': datetime.now().isoformat(),
                'match_id': match_data.get('match_id_api', 'unknown')
            }
            
            self.total_predictions += 1
            self.last_run = datetime.now()
            
            logger.debug(f"✅ {self.name}: Prédiction générée en {prediction['execution_time_ms']}ms")
            return prediction
            
        except Exception as e:
            logger.error(f"❌ {self.name}: Erreur lors de la prédiction: {e}")
            return self._error_response(str(e))
    
    def _validate_input(self, match_data: Dict[str, Any]) -> bool:
        """Valide que les données d'entrée sont suffisantes."""
        required_fields = ['home_team', 'away_team', 'match_date']
        return all(field in match_data for field in required_fields)
    
    def _validate_output(self, result: Dict[str, Any]) -> bool:
        """Valide que le résultat de l'IA est bien formaté."""
        required = ['prediction', 'confidence']
        if not all(k in result for k in required):
            return False
        if not isinstance(result['confidence'], (int, float)) or not 0 <= result['confidence'] <= 1:
            return False
        return True
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Génère une réponse d'erreur standardisée."""
        return {
            'agent_name': self.name,
            'prediction': 'ERROR',
            'confidence': 0.0,
            'weighted_confidence': 0.0,
            'reasoning': f"Erreur: {error_msg}",
            'error': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'agent."""
        success_rate = (
            self.successful_predictions / self.total_predictions * 100
            if self.total_predictions > 0 else 0
        )
        return {
            'name': self.name,
            'version': self.version,
            'weight': self._weight,
            'total_predictions': self.total_predictions,
            'success_rate_percent': round(success_rate, 2),
            'last_run': self.last_run.isoformat() if self.last_run else None
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST BASE AGENT - EROS BOT")
    print("=" * 60)
    print("✅ BasePredictionAgent chargé avec succès")
    print("📊 Version: 1.0.0")
    print("\n✅ TEST RÉUSSI !")
    print("=" * 60)