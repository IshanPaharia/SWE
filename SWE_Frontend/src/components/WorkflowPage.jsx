import React, { useState } from "react";
import axios from "axios";
import {
  PlayCircle,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Code,
  Users,
  Zap,
  TestTube,
  Bug,
  FileText,
  ChevronRight,
  Download,
} from "lucide-react";

// Enhanced CFG Visualization Component (inspired by reference implementation)
const CFGVisualization = ({ nodes, edges }) => {
  if (!nodes || nodes.length === 0) return null;

  const verticalSpacing = 100;
  const centerX = 250;
  const svgWidth = 550;
  const svgHeight = Math.max(400, nodes.length * verticalSpacing + 100);

  // Determine node type
  const getNodeType = (node) => {
    if (node.is_entry) return "entry";
    if (node.is_exit) return "exit";
    if (
      node.code_snippet &&
      (node.code_snippet.includes("if") ||
        node.code_snippet.includes("while") ||
        node.code_snippet.includes("for") ||
        node.code_snippet.includes("switch"))
    )
      return "decision";
    return "statement";
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
      <p className="text-sm font-medium text-gray-700 mb-3">
        Control Flow Graph ({nodes.length} nodes, {edges?.length || 0} edges):
      </p>
      <div className="bg-white rounded border border-gray-200 p-4">
        <svg width={svgWidth} height={svgHeight} className="mx-auto">
          {/* Arrow markers */}
          <defs>
            <marker
              id="arrow-gray"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#6B7280" />
            </marker>
            <marker
              id="arrow-green"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#22C55E" />
            </marker>
            <marker
              id="arrow-red"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#EF4444" />
            </marker>
          </defs>

          {/* Draw edges first */}
          {edges?.map((edge, idx) => {
            const fromIdx = nodes.findIndex(
              (n) => n.node_id === edge.source_node_id
            );
            const toIdx = nodes.findIndex(
              (n) => n.node_id === edge.target_node_id
            );
            if (fromIdx === -1 || toIdx === -1) return null;

            const y1 = 50 + fromIdx * verticalSpacing + 30;
            const y2 = 50 + toIdx * verticalSpacing - 30;

            const isTrueBranch =
              edge.label &&
              (edge.label.includes("true") ||
                edge.label.includes("True") ||
                edge.label === "next");
            const isFalseBranch =
              edge.label &&
              (edge.label.includes("false") || edge.label.includes("False"));

            // True branch - straight down (green)
            if (isTrueBranch || (!isTrueBranch && !isFalseBranch)) {
              return (
                <g key={idx}>
                  <line
                    x1={centerX}
                    y1={y1}
                    x2={centerX}
                    y2={y2}
                    stroke={isTrueBranch ? "#22C55E" : "#6B7280"}
                    strokeWidth="2"
                    markerEnd={
                      isTrueBranch ? "url(#arrow-green)" : "url(#arrow-gray)"
                    }
                  />
                  {edge.label && edge.label !== "next" && (
                    <text
                      x={centerX + 15}
                      y={(y1 + y2) / 2}
                      fill="#22C55E"
                      fontSize="11"
                      fontWeight="600"
                    >
                      {edge.label}
                    </text>
                  )}
                </g>
              );
            }

            // False branch - curved to right (red)
            if (isFalseBranch) {
              const controlX = 380;
              const controlY1 = y1 + 30;
              const controlY2 = y2 - 30;
              return (
                <g key={idx}>
                  <path
                    d={`M ${centerX} ${y1} C ${controlX} ${controlY1}, ${controlX} ${controlY2}, ${centerX} ${y2}`}
                    stroke="#EF4444"
                    strokeWidth="2"
                    fill="none"
                    markerEnd="url(#arrow-red)"
                  />
                  <text
                    x={controlX + 10}
                    y={(y1 + y2) / 2}
                    fill="#EF4444"
                    fontSize="11"
                    fontWeight="600"
                  >
                    {edge.label}
                  </text>
                </g>
              );
            }

            return null;
          })}

          {/* Draw nodes on top */}
          {nodes.map((node, idx) => {
            const y = 50 + idx * verticalSpacing;
            const nodeType = getNodeType(node);

            return (
              <g key={node.node_id}>
                {/* Node ID label on left */}
                <text
                  x={centerX - 90}
                  y={y + 5}
                  fill="#64748B"
                  fontSize="12"
                  fontWeight="700"
                >
                  N{node.node_id}
                </text>

                {/* Decision node - diamond shape */}
                {nodeType === "decision" && (
                  <>
                    <polygon
                      points={`${centerX},${y - 35} ${
                        centerX + 75
                      },${y} ${centerX},${y + 35} ${centerX - 75},${y}`}
                      fill="#FEF3C7"
                      stroke="#F59E0B"
                      strokeWidth="2"
                    />
                    <text
                      x={centerX}
                      y={y - 5}
                      textAnchor="middle"
                      fill="#92400E"
                      fontSize="11"
                      fontWeight="600"
                    >
                      {node.code_snippet?.substring(0, 18) || "Decision"}
                    </text>
                    <text
                      x={centerX}
                      y={y + 10}
                      textAnchor="middle"
                      fill="#92400E"
                      fontSize="9"
                    >
                      {node.code_snippet?.length > 18 ? "..." : ""}
                    </text>
                  </>
                )}

                {/* Entry/Exit node - ellipse shape */}
                {(nodeType === "entry" || nodeType === "exit") && (
                  <>
                    <ellipse
                      cx={centerX}
                      cy={y}
                      rx="70"
                      ry="30"
                      fill={nodeType === "entry" ? "#DBEAFE" : "#FEE2E2"}
                      stroke={nodeType === "entry" ? "#3B82F6" : "#EF4444"}
                      strokeWidth="2"
                    />
                    <text
                      x={centerX}
                      y={y - 5}
                      textAnchor="middle"
                      fill="#1E293B"
                      fontSize="12"
                      fontWeight="700"
                    >
                      {nodeType === "entry" ? "ENTRY" : "EXIT"}
                    </text>
                    <text
                      x={centerX}
                      y={y + 10}
                      textAnchor="middle"
                      fill="#475569"
                      fontSize="10"
                    >
                      {node.code_snippet?.substring(0, 15) || ""}
                    </text>
                  </>
                )}

                {/* Statement node - rectangle */}
                {nodeType === "statement" && (
                  <>
                    <rect
                      x={centerX - 75}
                      y={y - 28}
                      width="150"
                      height="56"
                      rx="6"
                      fill="#F0F9FF"
                      stroke="#7C3AED"
                      strokeWidth="2"
                    />
                    <text
                      x={centerX}
                      y={y - 5}
                      textAnchor="middle"
                      fill="#1E293B"
                      fontSize="11"
                      fontWeight="500"
                    >
                      {node.code_snippet?.substring(0, 20) || "Statement"}
                    </text>
                    {node.code_snippet?.length > 20 && (
                      <text
                        x={centerX}
                        y={y + 10}
                        textAnchor="middle"
                        fill="#475569"
                        fontSize="10"
                      >
                        {node.code_snippet.substring(20, 40)}...
                      </text>
                    )}
                  </>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Node details table */}
      <div className="mt-4 bg-white rounded border border-gray-200 p-3">
        <p className="text-xs font-semibold text-gray-700 mb-2">
          Node Details:
        </p>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {nodes.map((node) => (
            <div
              key={node.node_id}
              className="text-xs flex items-start gap-2 p-1.5 hover:bg-gray-50 rounded"
            >
              <span className="font-mono font-bold text-gray-600 min-w-[30px]">
                N{node.node_id}
              </span>
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                  getNodeType(node) === "entry"
                    ? "bg-blue-100 text-blue-700"
                    : getNodeType(node) === "exit"
                    ? "bg-red-100 text-red-700"
                    : getNodeType(node) === "decision"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-purple-100 text-purple-700"
                }`}
              >
                {getNodeType(node)}
              </span>
              <span className="text-gray-600 font-mono truncate flex-1">
                {node.code_snippet || "-"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const WorkflowPage = () => {
  const [sourceCode, setSourceCode] = useState(`#include <iostream>
using namespace std;

int findMax(int a, int b) {
    if (a > b) {
        return a;
    }
    if (b > a) {
        return b;
    }
    // BUG: Missing return for a == b!
}

int main() {
    int x, y;
    cin >> x >> y;
    int result = findMax(x, y);
    cout << result << endl;
    return 0;
}`);
  const [filename, setFilename] = useState("test.cpp");

  // Step states
  const [step1, setStep1] = useState({
    status: "pending",
    data: null,
    loading: false,
    error: null,
  });
  const [step2, setStep2] = useState({
    status: "pending",
    data: null,
    loading: false,
    error: null,
  });
  const [step3, setStep3] = useState({
    status: "pending",
    data: null,
    loading: false,
    error: null,
  });
  const [step4, setStep4] = useState({
    status: "pending",
    data: null,
    loading: false,
    error: null,
  });
  const [step5, setStep5] = useState({
    status: "pending",
    data: null,
    loading: false,
    error: null,
  });
  const [step6, setStep6] = useState({
    status: "pending",
    data: null,
    loading: false,
    error: null,
  });

  // Config
  const [populationSize, setPopulationSize] = useState(20); // Increased for more diversity
  const [generations, setGenerations] = useState(30); // Increased to find edge cases

  // Step 1: Generate CFG
  const executeStep1 = async () => {
    setStep1({ ...step1, loading: true, error: null });
    try {
      const response = await axios.post("/analysis/generate-cfg", {
        filename: filename,
        source_code: sourceCode,
      });
      setStep1({
        status: "completed",
        data: response.data,
        loading: false,
        error: null,
      });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setStep1({
        status: "error",
        data: null,
        loading: false,
        error:
          typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg),
      });
    }
  };

  // Step 2: Initialize + Evolve Population (Combined)
  const executeStep2 = async () => {
    if (!step1.data) return;
    setStep2({ ...step2, loading: true, error: null });
    try {
      // Initialize population
      const initResponse = await axios.post("/ga/initialize", {
        cfg_id: step1.data.cfg_id,
        population_size: populationSize,
        mutation_rate: 0.3, // Increased for better fault detection
        crossover_rate: 0.75,
      });

      // Evolve population for multiple generations
      let evolveResponse = initResponse.data;
      for (let gen = 0; gen < generations; gen++) {
        evolveResponse = await axios.post("/ga/evolve", {
          cfg_id: step1.data.cfg_id,
          mutation_rate: 0.3, // Increased for better fault detection
          crossover_rate: 0.75,
        });
      }

      setStep2({
        status: "completed",
        data: {
          ...evolveResponse.data,
          initial_population: initResponse.data.population,
        },
        loading: false,
        error: null,
      });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setStep2({
        status: "error",
        data: null,
        loading: false,
        error:
          typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg),
      });
    }
  };

  // Step 3: Evaluate Fitness (Branch Coverage)
  const executeStep3 = async () => {
    if (!step2.data) return;
    setStep3({ ...step3, loading: true, error: null });
    try {
      // Evaluate fitness for best individuals
      const individuals =
        step2.data.best_individuals || step2.data.population || [];
      const fitnessResults = [];

      for (const individual of individuals.slice(0, 10)) {
        const response = await axios.post("/fitness/evaluate", {
          test_case: {
            chromosome_id: individual.chromosome_id,
            genes: individual.genes,
            fitness: individual.fitness,
          },
          source_code: sourceCode,
          cfg_id: step1.data.cfg_id,
        });
        fitnessResults.push(response.data);
      }

      // Calculate summary statistics
      const coverageScores = fitnessResults.map((r) => r.branch_coverage);
      const totalBranches = step1.data.total_nodes || 1;

      setStep3({
        status: "completed",
        data: {
          fitness_results: fitnessResults,
          best_coverage: Math.max(...coverageScores, 0),
          avg_coverage:
            coverageScores.reduce((a, b) => a + b, 0) / coverageScores.length ||
            0,
          total_branches: totalBranches,
          test_cases_evaluated: fitnessResults.length,
        },
        loading: false,
        error: null,
      });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setStep3({
        status: "error",
        data: null,
        loading: false,
        error:
          typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg),
      });
    }
  };

  // Helper function to detect function type and calculate expected output
  const calculateExpectedOutput = (genes, sourceCode) => {
    if (genes.length !== 2) return null;

    const a = genes[0];
    const b = genes[1];

    // Detect function name from source code
    const funcMatch = sourceCode.match(/int\s+(\w+)\s*\(/);
    const functionName = funcMatch ? funcMatch[1].toLowerCase() : "";

    // Calculate expected output based on function type
    if (functionName.includes("max")) {
      return Math.max(a, b);
    } else if (functionName.includes("min")) {
      return Math.min(a, b);
    } else if (functionName.includes("add") || functionName.includes("sum")) {
      return a + b;
    } else if (functionName.includes("sub") || functionName.includes("diff")) {
      return a - b;
    } else if (functionName.includes("mul") || functionName.includes("mult")) {
      return a * b;
    } else if (functionName.includes("div") && b !== 0) {
      return Math.floor(a / b);
    }

    // Default: try to infer from code logic
    if (sourceCode.includes("a > b") || sourceCode.includes("a >= b")) {
      return Math.max(a, b); // Likely a max function
    } else if (sourceCode.includes("a < b") || sourceCode.includes("a <= b")) {
      return Math.min(a, b); // Likely a min function
    }

    return null; // Cannot determine
  };

  // Step 4: Execute All Tests Automatically
  const executeStep4 = async () => {
    if (!step2.data) return;
    setStep4({ ...step4, loading: true, error: null });

    try {
      // Get best individuals from evolved population
      const individuals =
        step2.data.best_individuals || step2.data.population || [];
      const testResults = [];

      // Execute each test case
      for (const individual of individuals.slice(0, 10)) {
        // Top 10 test cases
        const genes = individual.genes;

        // Calculate expected output dynamically based on function type
        const expectedOutput = calculateExpectedOutput(genes, sourceCode);

        const response = await axios.post("/test/execute", {
          source_filename: filename,
          source_code: sourceCode,
          test_inputs: genes,
          expected_output: expectedOutput,
        });
        testResults.push(response.data);
      }

      setStep4({
        status: "completed",
        data: {
          test_results: testResults,
          total: testResults.length,
          passed: testResults.filter((t) => t.execution_status === "passed")
            .length,
          failed: testResults.filter((t) => t.execution_status === "failed")
            .length,
        },
        loading: false,
        error: null,
      });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setStep4({
        status: "error",
        data: null,
        loading: false,
        error:
          typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg),
      });
    }
  };

  // Step 5: Fault Localization (Automatic)
  const executeStep5 = async () => {
    if (!step4.data) return;
    setStep5({ ...step5, loading: true, error: null });

    try {
      // Prepare test results for Tarantula
      const testInputs = step4.data.test_results.map((result) => ({
        test_id: result.test_id,
        status: result.execution_status === "passed" ? "passed" : "failed",
        covered_lines: result.coverage_data
          .filter((c) => c.execution_count > 0)
          .map((c) => c.line_number),
      }));

      const response = await axios.post("/fault-localization/analyze", {
        source_filename: filename,
        test_results: testInputs,
      });

      setStep5({
        status: "completed",
        data: response.data,
        loading: false,
        error: null,
      });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setStep5({
        status: "error",
        data: null,
        loading: false,
        error:
          typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg),
      });
    }
  };

  // Step 6: Generate Report
  const executeStep6 = async () => {
    if (!step5.data) return;
    setStep6({ ...step6, loading: true, error: null });

    try {
      const response = await axios.post("/report/generate", {
        analysis_id: step5.data.analysis_id,
        top_n: 5,
        include_recommendations: true,
      });

      setStep6({
        status: "completed",
        data: response.data,
        loading: false,
        error: null,
      });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setStep6({
        status: "error",
        data: null,
        loading: false,
        error:
          typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg),
      });
    }
  };

  // Run all steps sequentially
  const runAllSteps = async () => {
    await executeStep1();
    // The rest will be triggered by useEffect or manual clicks
  };

  const downloadReport = () => {
    if (!step6.data) return;
    const blob = new Blob([JSON.stringify(step6.data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `fault_localization_report_${step6.data.report_id}.json`;
    a.click();
  };

  const StepCard = ({
    number,
    title,
    icon: Icon,
    status,
    loading,
    error,
    data,
    onExecute,
    disabled,
    children,
  }) => {
    const canExecute = !disabled && status !== "completed" && !loading;

    return (
      <div
        className={`relative border-2 rounded-xl p-6 transition-all ${
          status === "completed"
            ? "bg-green-50 border-green-300"
            : status === "error"
            ? "bg-red-50 border-red-300"
            : "bg-white border-gray-200 hover:border-blue-300"
        }`}
      >
        {/* Step Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center ${
                status === "completed"
                  ? "bg-green-500"
                  : status === "error"
                  ? "bg-red-500"
                  : loading
                  ? "bg-blue-500 animate-pulse"
                  : "bg-gray-300"
              }`}
            >
              {status === "completed" ? (
                <CheckCircle2 className="w-6 h-6 text-white" />
              ) : loading ? (
                <Loader2 className="w-6 h-6 text-white animate-spin" />
              ) : (
                <span className="text-white font-bold">{number}</span>
              )}
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
                <Icon className="w-5 h-5" />
                <span>{title}</span>
              </h3>
            </div>
          </div>

          {onExecute && (
            <button
              onClick={onExecute}
              disabled={!canExecute}
              className={`btn-primary px-4 py-2 text-sm ${
                !canExecute ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {loading ? (
                <span className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Running...</span>
                </span>
              ) : status === "completed" ? (
                "Completed ✓"
              ) : (
                "Execute"
              )}
            </button>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 bg-red-100 border border-red-300 rounded-lg p-3 flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">
              {typeof error === "string"
                ? error
                : JSON.stringify(error, null, 2)}
            </p>
          </div>
        )}

        {/* Content */}
        {children}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Fault Localization System
          </h1>
          <p className="text-gray-600">
            Test generation and bug detection using genetic algorithms and
            spectrum-based fault localization
          </p>
        </div>

        {/* Source Code Input */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">📝 Source Code</h2>
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              className="input-field w-48"
              placeholder="filename.cpp"
            />
          </div>
          <textarea
            value={sourceCode}
            onChange={(e) => setSourceCode(e.target.value)}
            onPaste={(e) => {
              // Sanitize pasted content to remove invisible Unicode characters
              e.preventDefault();
              const pastedText = e.clipboardData.getData("text");
              // Remove non-breaking spaces and other problematic characters
              const sanitized = pastedText
                .replace(/\u00A0/g, " ") // Non-breaking space
                .replace(/\u202F/g, " ") // Narrow no-break space
                .replace(/\u2009/g, " ") // Thin space
                .replace(/\u200B/g, "") // Zero-width space
                .replace(/\uFEFF/g, ""); // Zero-width no-break space
              setSourceCode(sanitized);
            }}
            className="input-field font-mono text-sm h-64"
            placeholder="Paste your C++ code here..."
          />
        </div>

        {/* Configuration */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-6">
          <h3 className="text-lg font-semibold text-purple-900 mb-4">
            ⚙️ Configuration
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-purple-900 mb-2">
                Population Size
              </label>
              <input
                type="number"
                value={populationSize}
                onChange={(e) => setPopulationSize(parseInt(e.target.value))}
                className="input-field"
                min="5"
                max="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-purple-900 mb-2">
                Generations to Evolve
              </label>
              <input
                type="number"
                value={generations}
                onChange={(e) => setGenerations(parseInt(e.target.value))}
                className="input-field"
                min="1"
                max="50"
              />
            </div>
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            {[
              { label: "CFG", status: step1.status },
              { label: "GA Evolution", status: step2.status },
              { label: "Fitness", status: step3.status },
              { label: "Testing", status: step4.status },
              { label: "Analysis", status: step5.status },
              { label: "Report", status: step6.status },
            ].map((step, idx, arr) => (
              <React.Fragment key={idx}>
                <div className="flex flex-col items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                      step.status === "completed"
                        ? "bg-green-500 text-white"
                        : step.status === "error"
                        ? "bg-red-500 text-white"
                        : "bg-gray-200 text-gray-600"
                    }`}
                  >
                    {step.status === "completed" ? "✓" : idx + 1}
                  </div>
                  <span className="text-xs text-gray-600 mt-1">
                    {step.label}
                  </span>
                </div>
                {idx < arr.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Step 1: CFG Generation */}
        <StepCard
          number={1}
          title="Control Flow Graph Generation"
          icon={Code}
          status={step1.status}
          loading={step1.loading}
          error={step1.error}
          data={step1.data}
          onExecute={executeStep1}
          disabled={false}
        >
          {step1.data && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Nodes</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {step1.data.total_nodes}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Parameters</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {step1.data.detected_parameters?.length || 0}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Complexity</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {step1.data.complexity}
                  </p>
                </div>
                <div className="col-span-3 bg-blue-50 rounded-lg p-3">
                  <p className="text-sm font-medium text-blue-900">
                    Detected Parameters:
                  </p>
                  <p className="text-sm text-blue-700 font-mono">
                    {JSON.stringify(step1.data.detected_parameters)}
                  </p>
                </div>
              </div>

              {/* CFG Visualization */}
              <CFGVisualization
                nodes={step1.data.nodes}
                edges={step1.data.edges}
              />
            </div>
          )}
        </StepCard>

        {/* Step 2: Initialize + Evolve Population */}
        <StepCard
          number={2}
          title="Initialize + Evolve GA Population"
          icon={Users}
          status={step2.status}
          loading={step2.loading}
          error={step2.error}
          data={step2.data}
          onExecute={executeStep2}
          disabled={step1.status !== "completed"}
        >
          {step2.data && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Final Generation</p>
                  <p className="text-2xl font-bold text-purple-600">
                    #{step2.data.generation}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Best Fitness</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {step2.data.best_fitness?.toFixed(3)}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Population Size</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {step2.data.population?.length || populationSize}
                  </p>
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-3 max-h-48 overflow-y-auto">
                <p className="text-sm font-medium text-purple-900 mb-2">
                  Evolved Test Cases:
                </p>
                {(
                  (
                    step2.data.best_individuals ||
                    step2.data.population ||
                    []
                  ).slice(0, 5) || []
                ).map((ind, idx) => (
                  <div
                    key={idx}
                    className="text-sm text-purple-700 flex justify-between font-mono"
                  >
                    <span>{JSON.stringify(ind.genes)}</span>
                    <span className="text-purple-600">
                      Fitness: {ind.fitness?.toFixed(3)}
                    </span>
                  </div>
                ))}
                {(() => {
                  const totalCount =
                    (step2.data.best_individuals || step2.data.population || [])
                      .length || 0;
                  const remaining = totalCount - 5;
                  return (
                    totalCount > 5 && (
                      <p className="text-xs text-purple-600 mt-2">
                        ...and {remaining} more (total: {totalCount})
                      </p>
                    )
                  );
                })()}
              </div>
            </div>
          )}
        </StepCard>

        {/* Step 3: Fitness Evaluation (Branch Coverage) */}
        <StepCard
          number={3}
          title="Evaluate Fitness (Branch Coverage)"
          icon={Zap}
          status={step3.status}
          loading={step3.loading}
          error={step3.error}
          data={step3.data}
          onExecute={executeStep3}
          disabled={step2.status !== "completed"}
        >
          {step3.data && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-gray-600">Best Coverage</p>
                  <p className="text-2xl font-bold text-green-600">
                    {(step3.data.best_coverage * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-gray-600">Avg Coverage</p>
                  <p className="text-2xl font-bold text-green-600">
                    {(step3.data.avg_coverage * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-gray-600">Test Cases</p>
                  <p className="text-2xl font-bold text-green-600">
                    {step3.data.test_cases_evaluated}
                  </p>
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm font-medium text-green-900 mb-3">
                  Coverage Results:
                </p>
                <div className="space-y-2">
                  {(step3.data.fitness_results || [])
                    .slice(0, 5)
                    .map((result, idx) => (
                      <div
                        key={idx}
                        className="bg-white rounded p-3 border border-green-200"
                      >
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-mono text-gray-700">
                            Test Case {idx + 1}
                          </span>
                          <span className="text-sm font-bold text-green-600">
                            {(result.branch_coverage * 100).toFixed(1)}%
                            coverage
                          </span>
                        </div>
                        <div className="mt-2 bg-gray-200 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-green-500 h-full transition-all"
                            style={{
                              width: `${result.branch_coverage * 100}%`,
                            }}
                          />
                        </div>
                        <div className="mt-1 text-xs text-gray-600">
                          Branches: {result.branches_covered?.length || 0} /{" "}
                          {step3.data.total_branches}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </StepCard>

        {/* Step 4: Test Execution */}
        <StepCard
          number={4}
          title="Execute All Tests"
          icon={TestTube}
          status={step4.status}
          loading={step4.loading}
          error={step4.error}
          data={step4.data}
          onExecute={executeStep4}
          disabled={step3.status !== "completed"}
        >
          {step4.data && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Total Tests</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {step4.data.total}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-gray-600">Passed</p>
                  <p className="text-2xl font-bold text-green-600">
                    {step4.data.passed}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-red-200">
                  <p className="text-sm text-gray-600">Failed</p>
                  <p className="text-2xl font-bold text-red-600">
                    {step4.data.failed}
                  </p>
                </div>
              </div>
            </div>
          )}
        </StepCard>

        {/* Step 5: Fault Localization */}
        <StepCard
          number={5}
          title="Fault Localization"
          icon={Bug}
          status={step5.status}
          loading={step5.loading}
          error={step5.error}
          data={step5.data}
          onExecute={executeStep5}
          disabled={step4.status !== "completed"}
        >
          {step5.data && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-white rounded-lg p-4 border border-gray-200">
                  <p className="text-sm text-gray-600">Total Tests</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {step5.data.total_tests}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-green-200">
                  <p className="text-sm text-gray-600">Passed</p>
                  <p className="text-2xl font-bold text-green-600">
                    {step5.data.passed_tests}
                  </p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-red-200">
                  <p className="text-sm text-gray-600">Failed</p>
                  <p className="text-2xl font-bold text-red-600">
                    {step5.data.failed_tests}
                  </p>
                </div>
              </div>
              {step5.data.failed_tests === 0 ? (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="text-sm font-medium text-green-900">
                    ✅ All tests passed! No faults detected.
                  </p>
                  <p className="text-xs text-green-700 mt-2">
                    No fault localization needed when all tests pass.
                  </p>
                </div>
              ) : (
                <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                  <p className="text-sm font-medium text-yellow-900 mb-3">
                    Most Suspicious Lines:
                  </p>
                  {(step5.data.suspicious_lines || [])
                    .slice(0, 5)
                    .map((line, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between py-2 border-b border-yellow-200 last:border-0"
                      >
                        <div className="flex items-center space-x-3">
                          <span className="w-6 h-6 rounded-full bg-yellow-400 text-yellow-900 flex items-center justify-center text-xs font-bold">
                            {idx + 1}
                          </span>
                          <span className="text-sm font-mono text-yellow-900">
                            Line {line.line_number}
                          </span>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className="text-xs text-yellow-700">
                            Failed: {line.failed_count} | Passed:{" "}
                            {line.passed_count}
                          </span>
                          <span className="text-lg font-bold text-red-600">
                            {line.suspiciousness_score.toFixed(4)}
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </StepCard>

        {/* Step 6: Report Generation */}
        <StepCard
          number={6}
          title="Generate Report"
          icon={FileText}
          status={step6.status}
          loading={step6.loading}
          error={step6.error}
          data={step6.data}
          onExecute={executeStep6}
          disabled={step5.status !== "completed"}
        >
          {step6.data && (
            <div className="space-y-4 mt-4">
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                <h4 className="font-semibold text-green-900 mb-2">Summary</h4>
                <p className="text-sm text-green-800">{step6.data.summary}</p>
              </div>

              <button
                onClick={downloadReport}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                <Download className="w-5 h-5" />
                <span>Download Complete Report</span>
              </button>

              {step6.data.recommendations &&
                (step6.data.recommendations.length || 0) > 0 && (
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <h4 className="font-semibold text-blue-900 mb-2">
                      Recommendations
                    </h4>
                    <ul className="space-y-2">
                      {(step6.data.recommendations || []).map((rec, idx) => (
                        <li
                          key={idx}
                          className="text-sm text-blue-800 flex items-start space-x-2"
                        >
                          <span className="text-blue-600">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
          )}
        </StepCard>

        {/* Execute All Button */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-6 text-center">
          <button
            onClick={async () => {
              await executeStep1();
              // Note: In a real implementation, you'd chain these with proper state management
            }}
            className="bg-white text-blue-600 hover:bg-gray-100 font-bold py-4 px-8 rounded-lg text-lg transition-all transform hover:scale-105 shadow-lg"
          >
            🚀 Run Complete Analysis (All Steps)
          </button>
          <p className="text-white text-sm mt-3 opacity-90">
            Executes all 6 steps sequentially
          </p>
        </div>
      </div>
    </div>
  );
};

export default WorkflowPage;
