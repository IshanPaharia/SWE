import React, { useState } from 'react'
import axios from 'axios'
import { PlayCircle, Loader2, CheckCircle2, AlertCircle, Bug } from 'lucide-react'

const F5FaultLocalizer = ({ sharedData, updateSharedData }) => {
  const [testResults, setTestResults] = useState(`[
  {
    "test_id": "test_001",
    "status": "passed",
    "covered_lines": [1, 2, 3, 5, 7]
  },
  {
    "test_id": "test_002",
    "status": "failed",
    "covered_lines": [1, 2, 4, 5, 8]
  }
]`)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const parsedTestResults = JSON.parse(testResults)
      const response = await axios.post('/api/fault-localization/analyze', {
        source_file: 'test.cpp',
        test_results: parsedTestResults
      })
      
      setResult(response.data)
      updateSharedData({ analysisId: response.data.analysis_id })
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
          F5: Fault Localization (Tarantula)
        </h2>
        <p className="text-gray-600">
          Apply the Tarantula algorithm to identify suspicious code lines based on test results.
        </p>
      </div>

      {/* Input Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Test Results (JSON)
        </label>
        <textarea
          value={testResults}
          onChange={(e) => setTestResults(e.target.value)}
          className="textarea-field"
          rows={15}
          placeholder="Enter test results..."
        />
        <p className="text-xs text-gray-500 mt-2">
          Provide an array of test results with test_id, status (passed/failed), and covered_lines
        </p>
      </div>

      <button
        onClick={handleAnalyze}
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Analyzing...</span>
          </>
        ) : (
          <>
            <Bug className="w-5 h-5" />
            <span>Analyze with Tarantula</span>
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
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-2 text-red-800">
            <Bug className="w-5 h-5" />
            <h4 className="font-semibold">Fault Localization Complete!</h4>
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Analysis ID</p>
              <p className="text-sm font-mono font-semibold text-gray-900 truncate">
                {result.analysis_id}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Total Tests</p>
              <p className="text-2xl font-bold text-primary-600">
                {result.total_tests}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Failed</p>
              <p className="text-2xl font-bold text-red-600">
                {result.failed_tests}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Passed</p>
              <p className="text-2xl font-bold text-green-600">
                {result.passed_tests}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">
              Suspicious Lines (Ranked by Suspiciousness)
            </p>
            {result.suspicious_lines.length > 0 ? (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {result.suspicious_lines.map((line, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded border ${
                      line.suspiciousness_score > 0.8
                        ? 'bg-red-100 border-red-300'
                        : line.suspiciousness_score > 0.5
                        ? 'bg-orange-100 border-orange-300'
                        : 'bg-yellow-100 border-yellow-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <span className={`w-8 h-8 flex items-center justify-center rounded-full text-sm font-bold text-white ${
                          line.suspiciousness_score > 0.8
                            ? 'bg-red-600'
                            : line.suspiciousness_score > 0.5
                            ? 'bg-orange-600'
                            : 'bg-yellow-600'
                        }`}>
                          {idx + 1}
                        </span>
                        <div>
                          <p className="text-sm font-semibold text-gray-900">
                            Line {line.line_number}
                          </p>
                          <p className="text-xs text-gray-600">
                            Failed: {line.failed_coverage} | Passed: {line.passed_coverage}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-600">Suspiciousness</p>
                        <p className={`text-2xl font-bold ${
                          line.suspiciousness_score > 0.8
                            ? 'text-red-700'
                            : line.suspiciousness_score > 0.5
                            ? 'text-orange-700'
                            : 'text-yellow-700'
                        }`}>
                          {line.suspiciousness_score.toFixed(4)}
                        </p>
                      </div>
                    </div>
                    <pre className="code-block mt-2 text-xs">{line.line_content}</pre>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 py-4">
                No suspicious lines identified
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default F5FaultLocalizer

