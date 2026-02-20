#!/usr/bin/env python3
"""🎯 Eros Bot - Predictor Interface (Multi-Marchés Complets)"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys
import os

# ============================================
# 🚨 FIX IMPORT - ACODE ANDROID
# ============================================
sys.path.insert(0, '/sdcard/Eros_bot_app')

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv
    for env_path in [
        Path('/sdcard/Eros_bot_app/backend/.env'),
        Path('/sdcard/Eros_bot_app/.env'),
    ]:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            print(f"✅ .env chargé: {env_path}")
            break
except ImportError:
    print("⚠️ python-dotenv non installé (optionnel)")
# ============================================

# Import du Meta Orchestrator
from backend.app.ai_engine.agents.meta_orchestrator import MetaOrchestratorAgent

# Import Supabase (optionnel)
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase non disponible (pip install supabase)")


class ErosPredictor:
    """Interface principale pour générer des prédictions multi-marchés."""
    
    def __init__(self):
        """Initialise le Meta-Orchestrator et Supabase"""
        print("🧠 Initialisation de ErosPredictor...")
        
        self.meta_agent = MetaOrchestratorAgent(weight=1.5)
        print("✅ Meta-Orchestrator prêt")
        
        self.supabase = None
        if SUPABASE_AVAILABLE:
            try:
                supa_url = os.getenv("SUPABASE_URL")
                supa_key = os.getenv("SUPABASE_KEY")
                if supa_url and supa_key:
                    self.supabase = create_client(supa_url, supa_key)
                    print("✅ Supabase connecté")
            except Exception as e:
                print(f"⚠️ Supabase non connecté: {e}")
    
    def predict_match(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """✅ LIGNE 65 CORRIGÉE : match_data: Dict[str, Any]"""
        start_time = datetime.now()
        
        result = self.meta_agent.predict(match_data)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        prediction = {
            'match': f"{match_data.get('home_team', '?')} vs {match_data.get('away_team', '?')}",
            'league': match_data.get('league', 'Unknown'),
            'match_date': match_data.get('match_date', 'Unknown'),
            'best_market': result.get('market_type', 'Unknown'),
            'final_prediction': result['prediction'],
            'final_confidence': result['confidence'],
            'risk_level': result.get('risk_level', 'unknown'),
            'recommendation': result.get('recommendation', ''),
            'reasoning': result['reasoning'],
            'all_markets': result.get('all_markets', {}),
            'details': result.get('details', {}),
            'execution_time_ms': round(execution_time * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction
    
    def predict_today_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Génère des prédictions pour les matchs d'aujourd'hui."""
        print("\n" + "=" * 70)
        print("🎯 EROS BOT - PRÉDICTIONS DU JOUR (MULTI-MARCHÉS)")
        print("=" * 70)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 IA Actives: 4 (Statisticien, Forme, TimeSeries, Context)")
        print(f"📊 Marchés Analysés: 10+ (1N2, Buts, HT/FT, Corners, etc.)")
        print("=" * 70)
        
        if not self.supabase:
            print("⚠️ Supabase non connecté → Mode démo avec matchs fictifs")
            return self._demo_predictions(limit)
        
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            result = self.supabase.table('matches').select('*').gte('match_date', today).lte('match_date', today + 'T23:59:59').limit(limit).execute()
            
            matches = result.data if hasattr(result, 'data') else []
            
            if not matches:
                print(f"ℹ️ Aucun match trouvé pour {today}")
                return self._demo_predictions(limit)
            
            print(f"📊 {len(matches)} matchs trouvés en base\n")
            
        except Exception as e:
            print(f"⚠️ Erreur Supabase: {e}")
            matches = []
        
        predictions = []
        for i, match in enumerate(matches, 1):
            print(f"\n{'='*70}")
            print(f"[{i}/{len(matches)}] 🔍 Analyse: {match.get('home_team')} vs {match.get('away_team')}")
            print(f"{'='*70}")
            
            pred = self.predict_match(match)
            predictions.append(pred)
            
            self._display_prediction(pred)
        
        if self.supabase and predictions:
            self._save_predictions(predictions)
        
        self._display_summary(predictions)
        
        return predictions
    
    def _display_prediction(self, pred: Dict[str, Any]):
        """Affiche une prédiction de manière détaillée et lisible."""
        
        print("\n🏆 " + "=" * 60)
        print(f"   🎯 MEILLEUR MARCHÉ: {pred['best_market']}")
        print(f"   📊 PRÉDICTION: {pred['final_prediction']}")
        print(f"   🎯 CONFIANCE: {pred['final_confidence']*100:.1f}%")
        
        risk_icon = {"low": "✅", "medium": "⚠️", "high": "❌"}.get(pred['risk_level'], "⚪")
        print(f"   {risk_icon} RISQUE: {pred['risk_level'].upper()}")
        print(f"   💡 {pred['recommendation']}")
        print("🏆 " + "=" * 60)
        
        print("\n📊 TOP 5 DES MARCHÉS LES PLUS FIABLES:")
        print("-" * 60)
        
        all_markets = pred.get('all_markets', {})
        if all_markets:
            sorted_markets = sorted(all_markets.items(), key=lambda x: x[1]['confidence'], reverse=True)
            
            for i, (market, data) in enumerate(sorted_markets[:5], 1):
                if data['confidence'] >= 0.75:
                    icon = "🏆"
                elif data['confidence'] >= 0.65:
                    icon = "✅"
                elif data['confidence'] >= 0.55:
                    icon = "⚠️"
                else:
                    icon = "⚪"
                
                print(f"   {i}. {icon} {market:<25} → {data['prediction']:<20} ({data['confidence']*100:.1f}%)")
        
        print("\n⚽ PRÉDICTIONS DE BUTS EXACTS:")
        print("-" * 60)
        
        if 'EXACT_GOALS_HOME' in all_markets:
            home_goals = all_markets['EXACT_GOALS_HOME']
            print(f"   🏠 {pred['match'].split(' vs ')[0]}:")
            print(f"      → {home_goals['prediction']} ({home_goals['confidence']*100:.0f}%)")
            if 'distribution' in home_goals:
                dist = home_goals['distribution']
                dist_str = " | ".join([f"{k}b:{v*100:.0f}%" for k, v in dist.items() if v > 0.1])
                print(f"      📈 Distribution: {dist_str}")
        
        if 'EXACT_GOALS_AWAY' in all_markets:
            away_goals = all_markets['EXACT_GOALS_AWAY']
            print(f"   ✈️ {pred['match'].split(' vs ')[1]}:")
            print(f"      → {away_goals['prediction']} ({away_goals['confidence']*100:.0f}%)")
            if 'distribution' in away_goals:
                dist = away_goals['distribution']
                dist_str = " | ".join([f"{k}b:{v*100:.0f}%" for k, v in dist.items() if v > 0.1])
                print(f"      📈 Distribution: {dist_str}")
        
        print("\n⏱️ PRÉDICTIONS MI-TEMPS / FIN DE MATCH:")
        print("-" * 60)
        
        if 'HT_FT' in all_markets:
            ht_ft = all_markets['HT_FT']
            ht_ft_display = ht_ft['prediction'].replace('_', '/')
            print(f"   🔄 HT/FT: {ht_ft_display} ({ht_ft['confidence']*100:.0f}%)")
        
        if 'OVER_UNDER_HT' in all_markets:
            ht_goals = all_markets['OVER_UNDER_HT']
            print(f"   ⏱️ Buts 1ère MT: {ht_goals['prediction']} ({ht_goals['confidence']*100:.0f}%)")
        
        if 'OVER_UNDER_1.5' in all_markets:
            over_15 = all_markets['OVER_UNDER_1.5']
            print(f"   📊 Over/Under 1.5: {over_15['prediction']} ({over_15['confidence']*100:.0f}%)")
        
        if 'OVER_UNDER_2.5' in all_markets:
            over_25 = all_markets['OVER_UNDER_2.5']
            print(f"   📊 Over/Under 2.5: {over_25['prediction']} ({over_25['confidence']*100:.0f}%)")
        
        if 'OVER_UNDER_3.5' in all_markets:
            over_35 = all_markets['OVER_UNDER_3.5']
            print(f"   📊 Over/Under 3.5: {over_35['prediction']} ({over_35['confidence']*100:.0f}%)")
        
        if 'BTTS' in all_markets:
            btts = all_markets['BTTS']
            btts_display = btts['prediction'].replace('BTTS_', '')
            print(f"   ✅ Les 2 équipes marquent: {btts_display} ({btts['confidence']*100:.0f}%)")
        
        if 'DOUBLE_CHANCE' in all_markets:
            dc = all_markets['DOUBLE_CHANCE']
            print(f"   🛡️ Double Chance: {dc['prediction']} ({dc['confidence']*100:.0f}%)")
        
        if 'CORNERS' in all_markets:
            corners = all_markets['CORNERS']
            print(f"   🚩 Corners: {corners['prediction']} ({corners['confidence']*100:.0f}%)")
        
        if 'CARDS' in all_markets:
            cards = all_markets['CARDS']
            print(f"   🟨 Cartons: {cards['prediction']} ({cards['confidence']*100:.0f}%)")
        
        print(f"\n💭 {pred['reasoning']}")
        print(f"⏱️ Temps d'analyse: {pred['execution_time_ms']}ms")
    
    def _demo_predictions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Génère des prédictions démo si pas de matchs en base."""
        print("\n⚠️ MODE DÉMO (aucun match en base)\n")
        
        demo_matches = [
            {'home_team': 'PSG', 'away_team': 'Marseille', 'league': 'Ligue 1'},
            {'home_team': 'Real Madrid', 'away_team': 'Barcelona', 'league': 'La Liga'},
            {'home_team': 'Bayern Munich', 'away_team': 'Dortmund', 'league': 'Bundesliga'},
            {'home_team': 'Manchester City', 'away_team': 'Liverpool', 'league': 'Premier League'},
            {'home_team': 'Juventus', 'away_team': 'AC Milan', 'league': 'Serie A'},
        ]
        
        predictions = []
        for match in demo_matches[:limit]:
            pred = self.predict_match(match)
            predictions.append(pred)
            
            self._display_prediction(pred)
            print("\n" + "=" * 70)
        
        return predictions
    
    def _save_predictions(self, predictions: List[Dict[str, Any]]):
        """Sauvegarde les prédictions dans Supabase."""
        try:
            for pred in predictions:
                data = {
                    'match_id': pred.get('match'),
                    'league': pred.get('league'),
                    'best_market': pred.get('best_market'),
                    'prediction_type': pred['final_prediction'],
                    'confidence_score': pred['final_confidence'],
                    'risk_level': pred.get('risk_level'),
                    'status': 'pending',
                    'created_at': datetime.now().isoformat()
                }
                self.supabase.table('predictions').insert(data).execute()
            print(f"\n✅ {len(predictions)} prédictions sauvegardées dans Supabase")
        except Exception as e:
            print(f"\n⚠️ Erreur sauvegarde: {e}")
    
    def _display_summary(self, predictions: List[Dict[str, Any]]):
        """Affiche le résumé final des prédictions."""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ GÉNÉRAL DES PRÉDICTIONS")
        print("=" * 70)
        
        strong_bets = [p for p in predictions if p['risk_level'] == 'low']
        medium_bets = [p for p in predictions if p['risk_level'] == 'medium']
        risky_bets = [p for p in predictions if p['risk_level'] == 'high']
        
        print(f"✅ Fortes confiances (Risque faible): {len(strong_bets)}")
        print(f"⚠️ Confiances modérées (Risque moyen): {len(medium_bets)}")
        print(f"❌ À éviter (Risque élevé): {len(risky_bets)}")
        
        if predictions:
            print("\n🏆 TOP 3 MEILLEURES OPPORTUNITÉS DU JOUR")
            print("-" * 70)
            
            sorted_preds = sorted(predictions, key=lambda x: x['final_confidence'], reverse=True)
            for i, pred in enumerate(sorted_preds[:3], 1):
                print(f"\n   {i}. {pred['match']}")
                print(f"      🎯 Marché: {pred['best_market']}")
                print(f"      📊 Prédiction: {pred['final_prediction']}")
                print(f"      🎯 Confiance: {pred['final_confidence']*100:.1f}%")
                print(f"      💡 {pred['recommendation']}")
        
        print("\n" + "=" * 70)


# ============================================
# 🧪 TEST PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print("🎯 EROS BOT - PREDICTOR INTERFACE (MULTI-MARCHÉS)")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    predictor = ErosPredictor()
    predictions = predictor.predict_today_matches(limit=5)
    
    print("\n" + "=" * 70)
    print("✅ EROS BOT - TEST TERMINÉ")
    print("=" * 70)