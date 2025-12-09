import typing
import dataclasses

@dataclasses.dataclass
class DlrExpr:
    func_name: str
    args: typing.Union["DlrExpr", str]

class NgProcParsingError(Exception):
    pass

def parsing_helper_any(s: str, subparsers: typing.List[typing.Callable[[str], typing.Tuple[typing.Any, int]]]) -> typing.Tuple[typing.Any, int]:
    exceptions = []
    for fn in subparsers:
        try:
            result = fn(s)
            return result
        except Exception as e:
            exceptions.append(e)
            print(f'Exception in one of the options: {e}')
    raise NgProcParsingError(f'Unexpected `{s[0]}` - all subparsers failed: {", ".join(exceptions)}')

def parsing_helper_seq(s: str, seq_parsers: typing.List[typing.Callable[[str], typing.Tuple[typing.Any, int]]]) -> typing.Tuple[typing.List[typing.Any], int]:
    idx = 0
    result_list = []
    for fn in seq_parsers:
        curr_result = fn(s[idx:])
        result_list.append(curr_result[0])
        idx += curr_result[1]
    return (result_list, idx)

def parsing_helper_repeat(s: str, subparser: typing.Callable[[str], typing.Tuple[typing.Any, int]]) -> typing.Tuple[typing.List[typing.Any], int]:
    idx = 0
    result_list = []
    raised_exc = False
    while not raised_exc and idx < len(s):
        try:
            curr_result = subparser(s[idx:])
            result_list.append(curr_result[0])
            idx += curr_result[1]
        except Exception as e:
            raised_exc = True
            print(f'Exception in repeated element: {e}')
    return (result_list, idx)

def parse(s):
    # idx = 0
    # while idx < len(s):
    #     curr_result = parse_expr(s)
    #     idx += curr_result[1]
    return parsing_helper_repeat(s, parse_expr)

def parse_expr(s) -> typing.Tuple[typing.Union[DlrExpr, str], int]:
    # if s[0] == '$':
    #     return parse_dlrexpr(s)
    # elif s[0] == '\\':
    #     return parse_escape_seq(s)
    # else:
    #     return (s[0], 1)
    return parsing_helper_any(s, [parse_dlrexpr, parse_escape_seq, parse_char])

def parse_dlrexpr(s: str) -> typing.Tuple[DlrExpr, int]:
    # if s[0] != '$':
    #     raise NgProcParsingError(f'Expected dollar sign (`$`), got `{s[0]}`')
    # idx = 1
    # func_name = ''
    # while s[idx].isalnum() or s[idx] in ['_']:
    #     func_name += s[idx]
    #     idx += 1
    result = parsing_helper_seq(s, [
        lambda s: parse_const_char(s, '$'),
        parse_func_name,
        lambda s: parsing_helper_repeat(s, lambda s: parsing_helper_seq(s, [
            lambda s: parse_braces(s, True),
            lambda s: parsing_helper_repeat(s, parse_expr),
            lambda s: parse_braces(s, False)]))])
    return (DlrExpr(result[0][1], [x[1] for x in result[0][2]]), result[1])

def parse_const_char(s: str, ch: str) -> typing.Tuple[str, int]:
    if s[0] == ch:
        return (ch, 1)
    else:
        raise NgProcParsingError(f'Expected `{ch}`, got `{s[0]}`')

def parse_func_name(s: str) -> typing.Tuple[str, int]:
    idx = 0
    func_name = ''
    while s[idx].isalnum() or s[idx] in ['_']:
        func_name += s[idx]
        idx += 1
    return (func_name, idx)

def parse_braces(s, left) -> typing.Tuple[str, int]:
    braces = '{{' if left else '}}'
    if s[:2] == braces:
        return (braces, 2)
    else:
        raise NgProcParsingError(f'Expected `{braces[0]}`, got `{s[0]}`')

def parse_char(s) -> typing.Tuple[str, int]:
    if s[0] in ['{', '}', '$']:
        raise NgProcParsingError(f'Got unexpected special character `{s[0]}`')
    return (s[0], 1)

def parse_escape_seq(s: str) -> typing.Tuple[str, int]:
    result = parsing_helper_seq(s, [
        lambda s: parse_const_char(s, '\\'),
        parse_char])
    if result[0][1] == '{':
        escaped = '{'
    elif result[0][1] == '}':
        escaped = '}'
    elif result[0][1] == '$':
        escaped = '$'

    return (result[0][1], escaped)
