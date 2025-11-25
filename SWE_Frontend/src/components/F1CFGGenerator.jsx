import React, { useState } from 'react'
import axios from 'axios'
import { PlayCircle, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

const F1CFGGenerator = ({ sharedData, updateSharedData }) => {
  const [filename, setFilename] = useState('test.cpp')
  const [sourceCode, setSourceCode] = useState(
    `#include <iostream>\nusing namespace std;\n\nint add(int a, int b) {\n    if (a > b) {\n        return a;\n    }\n    return b;\n}\n\nint main() {\n    int x, y;\n    cin >> x >> y;\n    int result = add(x, y);\n    cout << result << endl;\n    return 0;\n}`
  )
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post('/api/analysis/generate-cfg', {
        filename,
        source_code: sourceCode
      })
      
      setResult(response.data)
      updateSharedData({ 
        cfgId: response.data.cfg_id, 
        sourceCode: sourceCode 
      })
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
          F1: Control Flow Graph Generation
        </h2>
        <p className="text-gray-600">
          Parse your C/C++ source code to generate a Control Flow Graph (CFG) and detect function parameters.
        </p>
      </div>

      {/* Input Section */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filename
          </label>
          <input
            type="text"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            className="input-field"
            placeholder="test.cpp"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Code
          </label>
          <textarea
            value={sourceCode}
            onChange={(e) => setSourceCode(e.target.value)}
            className="textarea-field"
            rows={15}
            placeholder="Enter your C/C++ code here..."
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading || !sourceCode.trim()}
          className="btn-primary w-full flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Generating CFG...</span>
            </>
          ) : (
            <>
              <PlayCircle className="w-5 h-5" />
              <span>Generate CFG</span>
            </>
          )}
        </button>
      </div>

      {/* Result Section */}
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
            <CheckCircle2 className="w-5 h-5" />
            <h4 className="font-semibold">CFG Generated Successfully!</h4>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">CFG ID</p>
              <p className="text-lg font-mono font-semibold text-gray-900 truncate">
                {result.cfg_id}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Total Nodes</p>
              <p className="text-2xl font-bold text-primary-600">
                {result.total_nodes}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Complexity</p>
              <p className="text-2xl font-bold text-purple-600">
                {result.complexity}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Parameters</p>
              <p className="text-2xl font-bold text-blue-600">
                {result.required_inputs.length}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Detected Parameters</p>
            <div className="flex flex-wrap gap-2">
              {result.required_inputs.map((param, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-mono"
                >
                  {param}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-2">CFG Nodes</p>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {result.nodes.map((node) => (
                <div
                  key={node.node_id}
                  className="flex items-center space-x-3 p-2 bg-gray-50 rounded border border-gray-200"
                >
                  <span className="w-8 h-8 flex items-center justify-center bg-primary-600 text-white rounded-full text-sm font-bold">
                    {node.node_id}
                  </span>
                  <span className="text-sm text-gray-700">{node.code_snippet}</span>
                  {node.is_entry && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">Entry</span>
                  )}
                  {node.is_exit && (
                    <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs">Exit</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default F1CFGGenerator

