#!/usr/bin/env python3
"""
🚀 Eros Bot - API Principale (FastAPI)
Point d'entrée pour le déploiement sur Render
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# Initialiser FastAPI
app = FastAPI(
    title="Eros Bot API",
    description="Prédictions football par Intelligence Artificielle",
    version="2.0"
)

# CORS pour autoriser Vercel et autres
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ROUTES ESSENTIELLES
# ============================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Eros Bot API - Running!",
        "version": "2.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Vérification de santé pour Render"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/predictions")
async def get_predictions():
    """
    Retourne les prédictions du jour.
    """
    mock_predictions = [
        {
            "match": "PSG vs Marseille",
            "league": "Ligue 1",
            "best_market": "DOUBLE_CHANCE",
            "final_prediction": "1N",
            "final_confidence": 0.785,
            "risk_level": "low",
            "recommendation": "✅ FORTE CONFIANCE - MEILLEUR MARCHÉ",
            "all_markets": {
                "DOUBLE_CHANCE": {"prediction": "1N", "confidence": 0.785},
                "OVER_UNDER_1.5": {"prediction": "OVER_1.5", "confidence": 0.723},
                "1N2": {"prediction": "HOME_WIN", "confidence": 0.685}
            }
        },
        {
            "match": "Real Madrid vs Barcelona",
            "league": "La Liga",
            "best_market": "BTTS",
            "final_prediction": "BTTS_YES",
            "final_confidence": 0.654,
            "risk_level": "medium",
            "recommendation": "⚠️ OPPORTUNITÉ MODÉRÉE",
            "all_markets": {
                "BTTS": {"prediction": "BTTS_YES", "confidence": 0.654},
                "1N2": {"prediction": "DRAW", "confidence": 0.582}
            }
        }
    ]
    
    return {
        "success": True,
        "count": len(mock_predictions),
        "predictions": mock_predictions,
        "generated_at": datetime.now().isoformat()
    }


# ============================================
# POINT D'ENTRÉE POUR UVICORN
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Démarrage de Eros Bot API sur le port {port}")
    print(f"📍 URLs disponibles:")
    print(f"   - http://localhost:{port}/")
    print(f"   - http://localhost:{port}/health")
    print(f"   - http://localhost:{port}/api/predictions")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
)
