import React, { useState } from 'react'
import axios from 'axios'
import { PlayCircle, Loader2, CheckCircle2, AlertCircle, TestTube } from 'lucide-react'

const F4TestExecutor = ({ sharedData, updateSharedData }) => {
  const [testInputs, setTestInputs] = useState('[42, -15]')
  const [expectedOutput, setExpectedOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleExecute = async () => {
    if (!sharedData.sourceCode) {
      setError('Please generate a CFG first (F1)')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const inputs = JSON.parse(testInputs)
      const response = await axios.post('/api/test/execute', {
        source_file: 'test.cpp',
        source_code: sharedData.sourceCode,
        test_inputs: inputs,
        expected_output: expectedOutput || null
      })
      
      setResult(response.data)
      
      // Update shared data with test result
      updateSharedData({
        testResults: [...(sharedData.testResults || []), response.data]
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
          F4: Test Execution with gcov
        </h2>
        <p className="text-gray-600">
          Execute tests with coverage instrumentation using GCC and gcov.
        </p>
      </div>

      {/* Prerequisites */}
      {sharedData.sourceCode ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
          <CheckCircle2 className="w-5 h-5 text-green-600" />
          <p className="text-sm text-green-800">Source code ready for testing</p>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-600" />
          <p className="text-sm text-yellow-800">Please generate a CFG first (F1)</p>
        </div>
      )}

      {/* Quick Test Guide */}
      {sharedData.sourceCode && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-purple-900 mb-2">💡 Quick Test Cases for findMax(a, b)</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
            <button
              onClick={() => {
                setTestInputs('[10, 5]')
                setExpectedOutput('10')
              }}
              className="bg-white hover:bg-purple-50 border border-purple-200 rounded px-3 py-2 text-left transition-colors"
            >
              <div className="font-mono text-purple-900">[10, 5]</div>
              <div className="text-purple-700">Expected: 10</div>
              <div className="text-purple-600">Case: a &gt; b</div>
            </button>
            <button
              onClick={() => {
                setTestInputs('[3, 8]')
                setExpectedOutput('8')
              }}
              className="bg-white hover:bg-purple-50 border border-purple-200 rounded px-3 py-2 text-left transition-colors"
            >
              <div className="font-mono text-purple-900">[3, 8]</div>
              <div className="text-purple-700">Expected: 8</div>
              <div className="text-purple-600">Case: b &gt; a</div>
            </button>
            <button
              onClick={() => {
                setTestInputs('[7, 7]')
                setExpectedOutput('7')
              }}
              className="bg-white hover:bg-red-50 border border-red-300 rounded px-3 py-2 text-left transition-colors"
            >
              <div className="font-mono text-red-900">[7, 7]</div>
              <div className="text-red-700">Expected: 7</div>
              <div className="text-red-600 font-semibold">⚠️ Bug: a == b</div>
            </button>
          </div>
        </div>
      )}

      {/* Input Section */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Test Inputs (JSON array)
          </label>
          <input
            type="text"
            value={testInputs}
            onChange={(e) => setTestInputs(e.target.value)}
            className="input-field font-mono"
            placeholder="[42, -15]"
          />
          <p className="text-xs text-gray-500 mt-1">
            Enter test inputs as a JSON array, e.g., [10, 20] or [5]
          </p>
        </div>

        <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
          <label className="block text-sm font-medium text-blue-900 mb-2 flex items-center space-x-2">
            <span>Expected Output</span>
            <span className="text-xs font-normal text-blue-700 bg-blue-200 px-2 py-0.5 rounded">IMPORTANT</span>
          </label>
          <input
            type="text"
            value={expectedOutput}
            onChange={(e) => setExpectedOutput(e.target.value)}
            className="input-field border-blue-300 focus:border-blue-500 focus:ring-blue-500"
            placeholder="What should the program output?"
          />
          <div className="mt-2 text-xs text-blue-800 space-y-1">
            <p className="font-medium">⚠️ Without expected output, tests will show as PASSED even if output is wrong!</p>
            <p>• For findMax(10, 5) → Expected output: <code className="bg-blue-100 px-1 rounded">10</code></p>
            <p>• For findMax(7, 7) → Expected output: <code className="bg-blue-100 px-1 rounded">7</code></p>
          </div>
        </div>

        <button
          onClick={handleExecute}
          disabled={loading || !sharedData.sourceCode}
          className="btn-primary w-full flex items-center justify-center space-x-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Executing Test...</span>
            </>
          ) : (
            <>
              <TestTube className="w-5 h-5" />
              <span>Execute Test</span>
            </>
          )}
        </button>
      </div>

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
        <div className={`border rounded-lg p-6 space-y-4 ${
          result.execution_status === 'passed' 
            ? 'bg-green-50 border-green-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {result.execution_status === 'passed' ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-600" />
              )}
              <h4 className={`font-semibold ${
                result.execution_status === 'passed' ? 'text-green-800' : 'text-red-800'
              }`}>
                Test {result.execution_status.toUpperCase()}
              </h4>
            </div>
            {result.execution_status === 'passed' && !expectedOutput && (
              <span className="text-xs bg-yellow-200 text-yellow-900 px-3 py-1 rounded-full font-medium">
                ⚠️ No validation (Expected output not provided)
              </span>
            )}
          </div>
          
          {result.execution_status === 'passed' && !expectedOutput && (
            <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-3">
              <p className="text-sm text-yellow-900 font-medium mb-1">⚠️ Warning: Test marked as PASSED without validation</p>
              <p className="text-xs text-yellow-800">
                The program ran successfully, but we don't know if the output is correct because 
                no expected output was specified. This test may hide bugs! 
                <br />
                <span className="font-semibold mt-1 inline-block">
                  Actual output was: <code className="bg-yellow-100 px-2 py-0.5 rounded">{result.output}</code>
                </span>
              </p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Test ID</p>
              <p className="text-sm font-mono font-semibold text-gray-900 truncate">
                {result.test_id}
              </p>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm text-gray-600">Execution Time</p>
              <p className="text-lg font-bold text-primary-600">
                {result.execution_time}s
              </p>
            </div>
          </div>

          {result.output && (
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Output</p>
              <pre className="code-block">{result.output}</pre>
            </div>
          )}

          {result.error && (
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Error</p>
              <pre className="code-block text-red-400">{result.error}</pre>
            </div>
          )}

          <div className="bg-white rounded-lg p-4">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Branches Taken ({result.branches_taken.length})
            </p>
            <div className="flex flex-wrap gap-2">
              {result.branches_taken.map((branch, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-mono"
                >
                  {branch}
                </span>
              ))}
            </div>
          </div>

          {result.coverage_data && result.coverage_data.length > 0 && (
            <div className="bg-white rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Coverage Data</p>
              <div className="space-y-1 max-h-64 overflow-y-auto">
                {result.coverage_data.map((cov, idx) => (
                  <div
                    key={idx}
                    className={`text-xs font-mono p-2 rounded ${
                      cov.execution_count > 0 
                        ? 'bg-green-50 text-green-900' 
                        : cov.execution_count === 0 
                        ? 'bg-red-50 text-red-900'
                        : 'bg-gray-50 text-gray-500'
                    }`}
                  >
                    <span className="inline-block w-12 text-right mr-3">
                      {cov.execution_count === -1 ? '-' : cov.execution_count}
                    </span>
                    <span className="inline-block w-12 text-right mr-3">
                      {cov.line_number}:
                    </span>
                    <span>{cov.source_line}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default F4TestExecutor

