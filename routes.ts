import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // En production: appeler ton backend Python sur Render
    // const res = await fetch('https://ton-api-render.onrender.com/api/predictions')
    
    // Pour le test: données mockées
    const mockPredictions = [
      {
        match: 'PSG vs Marseille',
        league: 'Ligue 1',
        best_market: 'DOUBLE_CHANCE',
        final_prediction: '1N',
        final_confidence: 0.785,
        risk_level: 'low',
        recommendation: '✅ FORTE CONFIANCE - MEILLEUR MARCHÉ',
        all_markets: {
          'DOUBLE_CHANCE': { prediction: '1N', confidence: 0.785 },
          'OVER_UNDER_1.5': { prediction: 'OVER_1.5', confidence: 0.723 },
          '1N2': { prediction: 'HOME_WIN', confidence: 0.685 },
        }
      },
      {
        match: 'Real Madrid vs Barcelona',
        league: 'La Liga',
        best_market: '1N2',
        final_prediction: 'DRAW',
        final_confidence: 0.582,
        risk_level: 'medium',
        recommendation: '⚠️ OPPORTUNITÉ MODÉRÉE',
        all_markets: {
          '1N2': { prediction: 'DRAW', confidence: 0.582 },
          'BTTS': { prediction: 'BTTS_YES', confidence: 0.654 },
        }
      },
    ]

    return NextResponse.json({ predictions: mockPredictions })
  } catch (error) {
    return NextResponse.json({ error: 'Erreur serveur' }, { status: 500 })
  }
}