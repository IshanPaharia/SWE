# Quick Start Guide

Get up and running with the Automated Test Case Generator in 5 minutes!

## Prerequisites

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **GCC/G++** - For coverage instrumentation
   - Windows: Install [MinGW-w64](https://www.mingw-w64.org/) or use [WSL](https://docs.microsoft.com/en-us/windows/wsl/)
   - Linux: `sudo apt-get install gcc g++`
   - macOS: `xcode-select --install`
3. **LLVM/Clang** - For C/C++ code parsing
   - Download from [LLVM Releases](https://releases.llvm.org/)
   - Add to PATH during installation

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure LibClang (Windows only)

If you get "LibClang not found" errors, edit `cfg_parser.py`:

```python
# Uncomment and set your LLVM path:
clang.cindex.Config.set_library_path(r'C:\Program Files\LLVM\bin')
```

### Step 3: Verify GCC and gcov

```bash
gcc --version
gcov --version
```

If these commands fail, install GCC/MinGW.

## Running the Server

### Option 1: Using Startup Scripts

**Windows:**
```bash
start_server.bat
```

**Linux/macOS:**
```bash
chmod +x start_server.sh
./start_server.sh
```

### Option 2: Manual Start

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## Quick Test

### 1. Open API Documentation

Navigate to: `http://localhost:8000/docs`

You'll see interactive API documentation with all endpoints.

### 2. Test F1: Generate CFG

Click on **POST /analysis/generate-cfg**, then "Try it out"

Paste this JSON:
```json
{
  "filename": "test.cpp",
  "source_code": "#include <iostream>\nint main() {\n    int x;\n    std::cin >> x;\n    if (x > 0) {\n        std::cout << \"positive\";\n    } else {\n        std::cout << \"negative\";\n    }\n    return 0;\n}"
}
```

Click "Execute" - you should get a CFG with nodes and edges!

### 3. Test F2: Initialize Population

Use the `cfg_id` from step 2 in **POST /ga/initialize**:

```json
{
  "cfg_id": "YOUR_CFG_ID_HERE",
  "population_size": 10
}
```

### 4. Run Complete Workflow

Run the example script:

```bash
python example_workflow.py
```

Choose option 2 to see fault localization in action!

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore all endpoints at `/docs`
- Check out test cases in `test/` directory
- Try different C/C++ programs

## Common Issues

### "LibClang not found"
- Install LLVM from https://releases.llvm.org/
- Set library path in `cfg_parser.py`

### "gcc: command not found"
- Install MinGW-w64 (Windows) or GCC (Linux/macOS)
- Add to PATH

### "ModuleNotFoundError"
- Run `pip install -r requirements.txt`

### Coverage data not generated
- Ensure source code compiles successfully
- Check that `.gcda` files are created in temp directory
- Try a simpler C++ program first

## Architecture Overview

```
Your C++ Code 
    ↓
F1: Parse & Generate CFG
    ↓
F2: Initialize GA Population (Test Cases)
    ↓
F4: Execute Tests with Coverage (gcov)
    ↓
F3: Evaluate Fitness (Branch Coverage)
    ↓
F2: Evolve Population (iterate)
    ↓
F5: Fault Localization (Tarantula)
    ↓
F6: Generate Report
```

## Support

For issues or questions:
1. Check the full README.md
2. Review API documentation at `/docs`
3. Examine example_workflow.py for usage patterns

## License

MIT License

---

**Ready to start?** Fire up the server and explore `/docs`! 🚀


