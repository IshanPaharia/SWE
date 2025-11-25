import React, { useState } from 'react'
import axios from 'axios'
import { PlayCircle, Loader2, CheckCircle2, AlertCircle, Activity } from 'lucide-react'

const F3FitnessEvaluator = ({ sharedData }) => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleEvaluate = async () => {
    if (!sharedData.cfgId) {
      setError('Please complete F1 and F2 first')
      return
    }

    if (!sharedData.sourceCode) {
      setError('Source code not found. Please go back to F1.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        `/api/fitness/evaluate-population?cfg_id=${sharedData.cfgId}&source_code=${encodeURIComponent(sharedData.sourceCode)}`
      )
      
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          F3: Fitness Evaluation
        </h2>
        <p className="text-gray-600">
          Evaluate test cases based on branch coverage metrics.
        </p>
      </div>

      {/* Prerequisites Check */}
      <div className="space-y-2">
        <div className={`flex items-center space-x-2 ${sharedData.cfgId ? 'text-green-600' : 'text-gray-400'}`}>
          <CheckCircle2 className="w-4 h-4" />
          <span className="text-sm">CFG Generated (F1)</span>
        </div>
        <div className={`flex items-center space-x-2 ${sharedData.cfgId ? 'text-green-600' : 'text-gray-400'}`}>
          <CheckCircle2 className="w-4 h-4" />
          <span className="text-sm">Population Initialized (F2)</span>
        </div>
      </div>

      <button
        onClick={handleEvaluate}
        disabled={loading || !sharedData.cfgId}
        className="btn-primary w-full flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Evaluating Fitness...</span>
          </>
        ) : (
          <>
            <Activity className="w-5 h-5" />
            <span>Evaluate Population Fitness</span>
          </>
        )}
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-red-900">Error</h4>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2 text-green-800">
            <Activity className="w-5 h-5" />
            <h4 className="font-semibold">Fitness Evaluation Complete!</h4>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Evaluated</p>
              <p className="text-2xl font-bold text-primary-600">
                {result.evaluated_count}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Best Fitness</p>
              <p className="text-2xl font-bold text-green-600">
                {result.best_fitness.toFixed(4)}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Avg Fitness</p>
              <p className="text-2xl font-bold text-blue-600">
                {result.avg_fitness.toFixed(4)}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Top Test Cases by Fitness</p>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {result.results
                .sort((a, b) => b.fitness_score - a.fitness_score)
                .slice(0, 10)
                .map((test, idx) => (
                  <div
                    key={test.test_case_id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="w-8 h-8 flex items-center justify-center bg-green-600 text-white rounded-full text-sm font-bold">
                        {idx + 1}
                      </span>
                      <div>
                        <p className="text-xs text-gray-500 font-mono">{test.test_case_id}</p>
                        <p className="text-sm text-gray-900">
                          {test.branches_covered.length} branches • {test.coverage_percentage.toFixed(1)}% coverage
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Fitness</p>
                      <p className="text-lg font-bold text-green-600">
                        {test.fitness_score.toFixed(4)}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default F3FitnessEvaluator

