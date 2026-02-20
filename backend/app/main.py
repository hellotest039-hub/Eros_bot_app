from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Eros Bot API", version="2.0")

# CORS pour autoriser Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Eros Bot API - Running!", "version": "2.0"}

@app.get("/api/predictions")
def get_predictions():
    return {
        "predictions": [
            {
                "match": "PSG vs Marseille",
                "league": "Ligue 1",
                "best_market": "DOUBLE_CHANCE",
                "final_prediction": "1N",
                "final_confidence": 0.785,
                "risk_level": "low",
                "recommendation": "✅ FORTE CONFIANCE",
                "all_markets": {
                    "DOUBLE_CHANCE": {"prediction": "1N", "confidence": 0.785},
                    "1N2": {"prediction": "HOME_WIN", "confidence": 0.685}
                }
            }
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
