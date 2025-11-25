import React, { useState } from 'react'
import axios from 'axios'
import { PlayCircle, Loader2, CheckCircle2, AlertCircle, GitBranch, Shuffle } from 'lucide-react'

const F2GAPopulation = ({ sharedData, updateSharedData }) => {
  const [populationSize, setPopulationSize] = useState(20)
  const [mutationRate, setMutationRate] = useState(0.15)
  const [crossoverRate, setCrossoverRate] = useState(0.75)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isEvolved, setIsEvolved] = useState(false)

  const handleInitialize = async () => {
    if (!sharedData.cfgId) {
      setError('Please generate a CFG first (F1)')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)
    setIsEvolved(false)

    try {
      const response = await axios.post('/api/ga/initialize', {
        cfg_id: sharedData.cfgId,
        population_size: populationSize
      })
      
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleEvolve = async () => {
    if (!sharedData.cfgId) {
      setError('Please initialize population first')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post('/api/ga/evolve', {
        cfg_id: sharedData.cfgId,
        mutation_rate: mutationRate,
        crossover_rate: crossoverRate
      })
      
      setResult(response.data)
      setIsEvolved(true)
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
          F2: Genetic Algorithm Population
        </h2>
        <p className="text-gray-600">
          Initialize a random population of test cases and evolve them using genetic operators.
        </p>
      </div>

      {/* CFG Status */}
      {sharedData.cfgId ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <CheckCircle2 className="w-5 h-5 text-green-600" />
          <div>
            <p className="text-sm font-medium text-green-900">CFG Ready</p>
            <p className="text-xs text-green-700 font-mono">{sharedData.cfgId}</p>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          <p className="text-sm text-yellow-800">Please generate a CFG first (F1)</p>
        </div>
      )}

      {/* Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Population Size
          </label>
          <input
            type="number"
            value={populationSize}
            onChange={(e) => setPopulationSize(parseInt(e.target.value))}
            className="input-field"
            min={5}
            max={1000}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mutation Rate
          </label>
          <input
            type="number"
            value={mutationRate}
            onChange={(e) => setMutationRate(parseFloat(e.target.value))}
            className="input-field"
            step={0.01}
            min={0}
            max={1}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Crossover Rate
          </label>
          <input
            type="number"
            value={crossoverRate}
            onChange={(e) => setCrossoverRate(parseFloat(e.target.value))}
            className="input-field"
            step={0.01}
            min={0}
            max={1}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={handleInitialize}
          disabled={loading || !sharedData.cfgId}
          className="btn-primary flex-1 flex items-center justify-center space-x-2"
        >
          {loading && !isEvolved ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Initializing...</span>
            </>
          ) : (
            <>
              <PlayCircle className="w-5 h-5" />
              <span>Initialize Population</span>
            </>
          )}
        </button>

        <button
          onClick={handleEvolve}
          disabled={loading || !result}
          className="btn-secondary flex-1 flex items-center justify-center space-x-2"
        >
          {loading && isEvolved ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Evolving...</span>
            </>
          ) : (
            <>
              <Shuffle className="w-5 h-5" />
              <span>Evolve Generation</span>
            </>
          )}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-red-900">Error</h4>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2 text-purple-800">
            <GitBranch className="w-5 h-5" />
            <h4 className="font-semibold">Population {isEvolved ? 'Evolved' : 'Initialized'}!</h4>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Generation</p>
              <p className="text-2xl font-bold text-purple-600">
                #{result.generation_id}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Population</p>
              <p className="text-2xl font-bold text-primary-600">
                {result.population_count}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Status</p>
              <p className="text-sm font-semibold text-green-600">
                {result.status}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Individuals (Test Cases)</p>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {result.individuals.slice(0, 20).map((individual, idx) => (
                <div
                  key={individual.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200"
                >
                  <div className="flex items-center space-x-3">
                    <span className="w-8 h-8 flex items-center justify-center bg-purple-600 text-white rounded-full text-sm font-bold">
                      {idx + 1}
                    </span>
                    <div>
                      <p className="text-xs text-gray-500 font-mono">{individual.id}</p>
                      <p className="text-sm font-mono text-gray-900">
                        Genes: [{individual.genes.join(', ')}]
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Fitness</p>
                    <p className="text-lg font-bold text-green-600">
                      {individual.fitness_score.toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
              {result.individuals.length > 20 && (
                <p className="text-center text-sm text-gray-500 py-2">
                  ... and {result.individuals.length - 20} more
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default F2GAPopulation

