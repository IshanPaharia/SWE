import cfg_parser


def test_cfg_parser_detects_function_and_if():
    src = """
    int foo(int a) {
        if (a > 0) return 1;
        return 0;
    }
    """

    res = cfg_parser.analyze_cpp_code(src)
    assert isinstance(res, dict)
    assert isinstance(res.get('nodes'), list)
    assert any('If Statement' in n.get('code_snippet', '') for n in res['nodes'])


def test_cfg_parser_parameters_extracted():
    src = 'int sum(int a, float b) { return a; }'
    res = cfg_parser.analyze_cpp_code(src)
    assert isinstance(res.get('params'), list)
    # Expect at least one parameter type like 'int' or 'float'
    assert any('int' in p or 'float' in p for p in res['params'])


def test_cfg_parser_handles_no_user_functions():
    # Code with only main or comments - parser should return structure
    src = 'int main() { return 0; }'
    res = cfg_parser.analyze_cpp_code(src)
    assert isinstance(res, dict)
    assert 'nodes' in res and 'edges' in res and 'params' in res
