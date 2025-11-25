# SWE Frontend - Automated Test Case Generator

Modern React + Tailwind CSS frontend for the Automated Test Case Generator API.

## Features

- **F1: CFG Generation** - Parse C/C++ code and generate Control Flow Graphs
- **F2: GA Population** - Initialize and evolve genetic algorithm populations
- **F3: Fitness Evaluation** - Evaluate test cases by branch coverage
- **F4: Test Execution** - Execute tests with gcov coverage instrumentation
- **F5: Fault Localization** - Apply Tarantula algorithm for fault detection
- **F6: Report Generation** - Generate comprehensive debugging reports

## Tech Stack

- **React 18.3** - Latest React with modern hooks
- **Vite 5** - Lightning-fast build tool
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon library

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
SWE_Frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx           # App header
│   │   ├── StepCard.jsx         # Step navigation cards
│   │   ├── F1CFGGenerator.jsx   # CFG generation
│   │   ├── F2GAPopulation.jsx   # GA population management
│   │   ├── F3FitnessEvaluator.jsx
│   │   ├── F4TestExecutor.jsx
│   │   ├── F5FaultLocalizer.jsx
│   │   └── F6ReportGenerator.jsx
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## API Configuration

The frontend proxies API requests through Vite. Requests to `/api/*` are forwarded to `http://localhost:8000`.

To change the backend URL, edit `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url:port',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## Usage Workflow

1. **F1**: Paste your C/C++ code and generate a CFG
2. **F2**: Initialize a population of test cases, then evolve them
3. **F3**: Evaluate the fitness of your test population
4. **F4**: Execute individual tests with coverage analysis
5. **F5**: Run fault localization on test results
6. **F6**: Generate and download comprehensive reports

## Development

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## License

MIT

