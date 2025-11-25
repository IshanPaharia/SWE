import clang.cindex
from typing import Dict, Any
import re
import sys
import os

# --- Configure LibClang library path ---
LLVM_PATHS = [
    r'C:\Program Files\LLVM\bin',
    r'C:\Program Files (x86)\LLVM\bin',
    r'C:\LLVM\bin',
]

libclang_configured = False
for path in LLVM_PATHS:
    if os.path.exists(path):
        try:
            clang.cindex.Config.set_library_path(path)
            # Test if it works
            clang.cindex.Index.create()
            libclang_configured = True
            print(f"LibClang configured successfully: {path}", file=sys.stderr)
            break
        except Exception as e:
            print(f"Failed to configure LibClang at {path}: {e}", file=sys.stderr)
            continue

if not libclang_configured:
    print("LibClang not available - using regex parser", file=sys.stderr)

def analyze_cpp_code(source_code: str) -> Dict[str, Any]:
    """
    Parses C++ code using LibClang with fallback to regex parsing.
    Returns: nodes, edges, and detected parameters.
    """
    # Try LibClang first
    try:
        return _parse_with_libclang(source_code)
    except Exception:
        # Silently fall back to regex parser
        return _parse_with_regex(source_code)


def _parse_with_libclang(source_code: str) -> Dict[str, Any]:
    """Parse using LibClang"""
    index = clang.cindex.Index.create()
    args = ['-std=c++11']
    unsaved_files = [('temp.cpp', source_code)]
    
    try:
        tu = index.parse('temp.cpp', args=args, unsaved_files=unsaved_files)
    except Exception as e:
        raise Exception(f"Clang Parse Error: {e}")

    nodes = []
    edges = []
    params = []
    user_function_found = False

    # Mapping Clang Cursors to readable names
    control_cursors = {
        clang.cindex.CursorKind.IF_STMT: "If Statement",
        clang.cindex.CursorKind.FOR_STMT: "For Loop",
        clang.cindex.CursorKind.WHILE_STMT: "While Loop",
        clang.cindex.CursorKind.SWITCH_STMT: "Switch Case",
        clang.cindex.CursorKind.RETURN_STMT: "Return",
        clang.cindex.CursorKind.FUNCTION_DECL: "Function Entry",
        clang.cindex.CursorKind.VAR_DECL: "Variable Decl"
    }

    node_counter = 1

    def is_from_source_file(cursor):
        """Check if cursor is from the actual source code (not system headers)"""
        if cursor.location.file is None:
            return False
        # Check if it's our temp file (not system headers)
        filename = cursor.location.file.name
        return 'temp.cpp' in filename or not ('include' in filename or 'bits' in filename or 'mingw' in filename)

    def walk_ast(cursor, parent_id=None):
        nonlocal node_counter, user_function_found
        current_id = None

        # Skip system headers but allow processing
        if cursor.location.file is not None:
            filename = cursor.location.file.name
            # Skip obvious system headers
            if any(sys_path in filename.lower() for sys_path in ['include', 'bits', 'mingw', 'msvc', 'windows kits']):
                return

        # LOGIC 1: Detect Function Arguments (Required for F2)
        if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # Skip main function
            if cursor.spelling != 'main':
                user_function_found = True
                for child in cursor.get_children():
                    if child.kind == clang.cindex.CursorKind.PARM_DECL:
                        # Capture the type (e.g., "int")
                        params.append(child.type.spelling)

        # LOGIC 2: Build Control Flow Graph (Required for F1)
        if cursor.kind in control_cursors:
            current_id = node_counter
            node_counter += 1
            
            nodes.append({
                "node_id": current_id,
                "code_snippet": control_cursors[cursor.kind],
                "is_entry": cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL,
                "is_exit": cursor.kind == clang.cindex.CursorKind.RETURN_STMT
            })
            
            if parent_id is not None:
                edges.append({
                    "source_node_id": parent_id,
                    "target_node_id": current_id,
                    "label": "next"
                })
        
        # Helper to pass the correct parent ID down the tree
        next_parent = current_id if current_id is not None else parent_id
        
        for child in cursor.get_children():
            walk_ast(child, next_parent)

    walk_ast(tu.cursor)
    
    # If LibClang found nothing, fall back to regex
    if len(nodes) == 0 and len(params) == 0:
        raise Exception("LibClang returned no results")
    
    return {"nodes": nodes, "edges": edges, "params": params}


def _parse_with_regex(source_code: str) -> Dict[str, Any]:
    """
    Fallback regex-based parser when LibClang is unavailable.
    Simple but effective for basic C++ code.
    """
    nodes = []
    edges = []
    params = []
    node_counter = 1
    
    # Find function parameters first (process entire source, not line by line)
    # Match patterns like: int functionName(int a, int b)
    func_pattern = r'\b(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
    for match in re.finditer(func_pattern, source_code):
        return_type = match.group(1)
        func_name = match.group(2)
        param_str = match.group(3).strip()
        
        # Skip main function and control structures
        if func_name in ['if', 'while', 'for', 'switch', 'main']:
            continue
            
        # Extract parameters
        if param_str and param_str != 'void' and param_str != '':
            # Parse parameters like "int a, float b"
            param_parts = param_str.split(',')
            for param in param_parts:
                param = param.strip()
                if param and param != '':
                    # Extract type (everything before the last word)
                    parts = param.split()
                    if len(parts) >= 2:
                        param_type = ' '.join(parts[:-1])  # Everything except variable name
                        params.append(param_type)
    
    # Split source into lines for control flow analysis
    lines = source_code.split('\n')
    
    # Find control flow structures and create nodes
    current_line = 0
    for line in lines:
        current_line += 1
        stripped = line.strip()
        
        # Function declarations
        if re.search(r'\b\w+\s+\w+\s*\([^)]*\)\s*\{', line):
            nodes.append({
                "node_id": node_counter,
                "code_snippet": "Function Entry",
                "is_entry": True,
                "is_exit": False
            })
            node_counter += 1
        
        # If statements
        elif stripped.startswith('if') and '(' in stripped:
            nodes.append({
                "node_id": node_counter,
                "code_snippet": "If Statement",
                "is_entry": False,
                "is_exit": False
            })
            node_counter += 1
        
        # For loops
        elif stripped.startswith('for') and '(' in stripped:
            nodes.append({
                "node_id": node_counter,
                "code_snippet": "For Loop",
                "is_entry": False,
                "is_exit": False
            })
            node_counter += 1
        
        # While loops
        elif stripped.startswith('while') and '(' in stripped:
            nodes.append({
                "node_id": node_counter,
                "code_snippet": "While Loop",
                "is_entry": False,
                "is_exit": False
            })
            node_counter += 1
        
        # Switch statements
        elif stripped.startswith('switch') and '(' in stripped:
            nodes.append({
                "node_id": node_counter,
                "code_snippet": "Switch Case",
                "is_entry": False,
                "is_exit": False
            })
            node_counter += 1
        
        # Return statements
        elif stripped.startswith('return'):
            nodes.append({
                "node_id": node_counter,
                "code_snippet": "Return",
                "is_entry": False,
                "is_exit": True
            })
            node_counter += 1
    
    # Create simple edges (sequential)
    for i in range(len(nodes) - 1):
        edges.append({
            "source_node_id": nodes[i]["node_id"],
            "target_node_id": nodes[i + 1]["node_id"],
            "label": "next"
        })
    
    return {"nodes": nodes, "edges": edges, "params": params}