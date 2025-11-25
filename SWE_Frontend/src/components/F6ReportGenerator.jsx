import React, { useState } from 'react'
import axios from 'axios'
import { PlayCircle, Loader2, CheckCircle2, AlertCircle, FileText, Download } from 'lucide-react'

const F6ReportGenerator = ({ sharedData }) => {
  const [topN, setTopN] = useState(10)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    if (!sharedData.analysisId) {
      setError('Please complete fault localization first (F5)')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post('/api/report/generate', {
        analysis_id: sharedData.analysisId,
        top_n: topN
      })
      
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadText = async () => {
    if (!result) return

    try {
      const response = await axios.get(`/api/report/${result.report_id}/text`, {
        responseType: 'text'
      })
      
      const blob = new Blob([response.data], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `fault-report-${result.report_id}.txt`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert('Failed to download report: ' + err.message)
    }
  }

  return (
    <div className="card space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          F6: Report Generation
        </h2>
        <p className="text-gray-600">
          Generate a comprehensive fault localization report with actionable recommendations.
        </p>
      </div>

      {/* Prerequisites Check */}
      {sharedData.analysisId ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <CheckCircle2 className="w-5 h-5 text-green-600" />
          <div>
            <p className="text-sm font-medium text-green-900">Analysis Ready</p>
            <p className="text-xs text-green-700 font-mono">{sharedData.analysisId}</p>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          <p className="text-sm text-yellow-800">Please complete fault localization first (F5)</p>
        </div>
      )}

      {/* Configuration */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Top N Suspicious Lines
        </label>
        <input
          type="number"
          value={topN}
          onChange={(e) => setTopN(parseInt(e.target.value))}
          className="input-field"
          min={1}
          max={100}
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={loading || !sharedData.analysisId}
        className="btn-primary w-full flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Generating Report...</span>
          </>
        ) : (
          <>
            <FileText className="w-5 h-5" />
            <span>Generate Report</span>
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
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-indigo-800">
              <FileText className="w-5 h-5" />
              <h4 className="font-semibold">Report Generated!</h4>
            </div>
            <button
              onClick={handleDownloadText}
              className="btn-secondary text-sm flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Report ID</p>
              <p className="text-sm font-mono font-semibold text-gray-900 truncate">
                {result.report_id}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Generated At</p>
              <p className="text-sm font-semibold text-gray-900">
                {new Date(result.generated_at).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Summary</p>
            <p className="text-sm text-gray-900">{result.summary}</p>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Top Suspicious Lines</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3">Rank</th>
                    <th className="text-left py-2 px-3">Line</th>
                    <th className="text-left py-2 px-3">Score</th>
                    <th className="text-left py-2 px-3">Failed</th>
                    <th className="text-left py-2 px-3">Passed</th>
                    <th className="text-left py-2 px-3">Code</th>
                  </tr>
                </thead>
                <tbody>
                  {result.top_suspicious_lines.map((line, idx) => (
                    <tr key={idx} className="border-b hover:bg-gray-50">
                      <td className="py-2 px-3 font-bold">{idx + 1}</td>
                      <td className="py-2 px-3 font-mono">{line.line_number}</td>
                      <td className="py-2 px-3">
                        <span className={`font-bold ${
                          line.suspiciousness_score > 0.8
                            ? 'text-red-600'
                            : line.suspiciousness_score > 0.5
                            ? 'text-orange-600'
                            : 'text-yellow-600'
                        }`}>
                          {line.suspiciousness_score.toFixed(4)}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-red-600">{line.failed_coverage}</td>
                      <td className="py-2 px-3 text-green-600">{line.passed_coverage}</td>
                      <td className="py-2 px-3 font-mono text-xs truncate max-w-xs">
                        {line.line_content}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Recommendations</p>
            <ul className="space-y-2">
              {result.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start space-x-3 text-sm">
                  <span className="w-6 h-6 flex-shrink-0 flex items-center justify-center bg-indigo-600 text-white rounded-full font-bold text-xs">
                    {idx + 1}
                  </span>
                  <p className="text-gray-700 pt-0.5">{rec}</p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default F6ReportGenerator

