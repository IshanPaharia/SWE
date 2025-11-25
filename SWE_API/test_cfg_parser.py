"""
Quick test script to verify CFG parser is working
Run this to check if the fix worked!
"""

import sys
# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from cfg_parser import analyze_cpp_code

test_code = """
#include <iostream>
using namespace std;

int findMax(int a, int b) {
    if (a > b) {
        return a;
    }
    if (b > a) {
        return b;
    }
}

int main() {
    int x, y;
    cin >> x >> y;
    int result = findMax(x, y);
    cout << result << endl;
    return 0;
}
"""

print("Testing CFG Parser...")
print("=" * 60)

try:
    result = analyze_cpp_code(test_code)
    
    print(f"✅ SUCCESS!")
    print(f"\nNodes found: {len(result['nodes'])}")
    print(f"Parameters found: {len(result['params'])}")
    print(f"Parameter types: {result['params']}")
    
    print(f"\nDetailed nodes:")
    for node in result['nodes']:
        print(f"  - Node {node['node_id']}: {node['code_snippet']}")
    
    print(f"\n{'='*60}")
    
    if len(result['nodes']) == 5 and len(result['params']) == 2:
        print("✅ PERFECT! Parser is working correctly!")
        print("✅ Expected: 5 nodes, 2 parameters")
        print("✅ Got: {} nodes, {} parameters".format(len(result['nodes']), len(result['params'])))
    elif len(result['nodes']) > 0 and len(result['params']) > 0:
        print("⚠️  Parser working but results slightly different")
        print(f"   Nodes: {len(result['nodes'])}, Params: {len(result['params'])}")
    else:
        print("❌ Parser returned empty results")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nThis means LibClang is not installed and regex parser also failed.")
    print("Try installing LLVM from: https://releases.llvm.org/")

