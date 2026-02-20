'use client'

import { useState, useEffect } from 'react'
import { Trophy, TrendingUp, Activity, Shield, Zap } from 'lucide-react'

interface Prediction {
  match: string
  league: string
  best_market: string
  final_prediction: string
  final_confidence: number
  risk_level: string
  recommendation: string
  all_markets: Record<string, { prediction: string; confidence: number }>
}

export default function Home() {
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ total: 0, high: 0, medium: 0, low: 0 })

  useEffect(() => {
    fetchPredictions()
    const interval = setInterval(fetchPredictions, 60000) // Refresh chaque minute
    return () => clearInterval(interval)
  }, [])

  const fetchPredictions = async () => {
    try {
      const res = await fetch('/api/predictions')
      const data = await res.json()
      setPredictions(data.predictions || [])
      
      const high = data.predictions?.filter((p: Prediction) => p.risk_level === 'low').length || 0
      const medium = data.predictions?.filter((p: Prediction) => p.risk_level === 'medium').length || 0
      const low = data.predictions?.filter((p: Prediction) => p.risk_level === 'high').length || 0
      
      setStats({ total: data.predictions?.length || 0, high, medium, low })
    } catch (error) {
      console.error('Erreur:', error)
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceClass = (confidence: number) => {
    if (confidence >= 0.75) return 'confidence-high'
    if (confidence >= 0.55) return 'confidence-medium'
    return 'confidence-low'
  }

  const getRiskIcon = (risk: string) => {
    switch(risk) {
      case 'low': return <Shield className="w-5 h-5 text-green-500" />
      case 'medium': return <Activity className="w-5 h-5 text-yellow-500" />
      default: return <Zap className="w-5 h-5 text-red-500" />
    }
  }

  return (
    <main className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Trophy className="w-10 h-10 text-primary" />
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            Eros Bot
          </h1>
        </div>
        <p className="text-gray-400">Prédictions Football par Intelligence Artificielle</p>
      </header>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="card-gradient rounded-xl p-4">
          <div className="text-3xl font-bold">{stats.total}</div>
          <div className="text-sm text-gray-400">Matchs Analysés</div>
        </div>
        <div className="card-gradient rounded-xl p-4">
          <div className="text-3xl font-bold text-green-500">{stats.high}</div>
          <div className="text-sm text-gray-400">Fortes Confiances</div>
        </div>
        <div className="card-gradient rounded-xl p-4">
          <div className="text-3xl font-bold text-yellow-500">{stats.medium}</div>
          <div className="text-sm text-gray-400">Confiances Modérées</div>
        </div>
        <div className="card-gradient rounded-xl p-4">
          <div className="text-3xl font-bold text-red-500">{stats.low}</div>
          <div className="text-sm text-gray-400">À Éviter</div>
        </div>
      </div>

      {/* Predictions List */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold">Prédictions du Jour</h2>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">Chargement...</div>
        ) : predictions.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            Aucune prédiction disponible pour le moment
          </div>
        ) : (
          <div className="space-y-4">
            {predictions.map((pred, index) => (
              <div key={index} className="card-gradient rounded-xl p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="text-sm text-primary font-semibold mb-1">{pred.league}</div>
                    <div className="text-xl font-bold mb-2">{pred.match}</div>
                    <div className="flex flex-wrap gap-2">
                      <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
                        🎯 {pred.best_market}
                      </span>
                      <span className="px-3 py-1 bg-secondary/20 text-secondary rounded-full text-sm">
                        📊 {pred.final_prediction}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <div className={`text-3xl font-bold ${getConfidenceClass(pred.final_confidence)}`}>
                        {(pred.final_confidence * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-400">Confiance</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getRiskIcon(pred.risk_level)}
                      <span className="text-sm text-gray-400 capitalize">{pred.risk_level}</span>
                    </div>
                  </div>
                </div>

                {/* Top Markets */}
                {pred.all_markets && (
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <div className="text-sm text-gray-400 mb-2">Top 3 Marchés:</div>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(pred.all_markets)
                        .sort((a, b) => b[1].confidence - a[1].confidence)
                        .slice(0, 3)
                        .map(([market, data]) => (
                          <span key={market} className="px-3 py-1 bg-white/5 rounded-lg text-sm">
                            {market}: {data.prediction} ({(data.confidence * 100).toFixed(0)}%)
                          </span>
                        ))}
                    </div>
                  </div>
                )}

                {/* Recommendation */}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className={`text-sm ${
                    pred.risk_level === 'low' ? 'text-green-500' :
                    pred.risk_level === 'medium' ? 'text-yellow-500' : 'text-red-500'
                  }`}>
                    💡 {pred.recommendation}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="mt-12 text-center text-gray-500 text-sm">
        <p>Eros Bot v2.0 - Propulsé par 4 IA + Auto-Training</p>
        <p className="mt-1">Les paris sportifs comportent des risques. Jouez responsablement.</p>
      </footer>
    </main>
  )
}
