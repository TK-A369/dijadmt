import pathlib
import typing
import shutil
import re
import os

from . import conf_reader
from . import ngproc_parser
from . import cli_parsing

def process_none(
        path_in: pathlib.Path,
        path_working: pathlib.Path,
        conf: conf_reader.Conf,
        common_options: cli_parsing.CliCommonOptions):
    if common_options.use_symlinks:
        os.symlink(path_in, path_working)
    else:
        # path_in.copy(path_working)
        shutil.copy(path_in, path_working)

def process_defsubs(
        path_in: pathlib.Path,
        path_working: pathlib.Path,
        conf: conf_reader.Conf,
        common_options: cli_parsing.CliCommonOptions):
    with path_in.open('r') as f_in, path_working.open('w') as f_working:
        s_in = f_in.read()
        s_subs = re.sub(
            r'\$dijadmt_if{([a-zA-Z0-9_]+)}{([^{}]*)}{([^{}]*)}',
            lambda m: m.group(3).strip() if conf.get_def(m.group(1)) == m.group(2) else "",
            s_in)
        s_subs = re.sub(
            r'\$dijadmt_def{([a-zA-Z0-9_]+)}',
            lambda m: v if (v := conf.get_def(m.group(1))) is not None else conf_reader.raiser(conf_reader.VariableUndefinedError(m.group(1))),
            s_subs)
        s_subs = re.sub(
            r'\$dijadmt_escape{(.)}',
            lambda m: m.group(1),
            s_subs)
        f_working.write(s_subs)

class NgProcEvalError(Exception):
    pass

# New Generation Processor
def process_ngproc(
        path_in: pathlib.Path,
        path_working: pathlib.Path,
        conf: conf_reader.Conf,
        common_options: cli_parsing.CliCommonOptions):
    def ast_eval(ast_node):
        if isinstance(ast_node, list):
            return ''.join(map(ast_eval, ast_node))
        elif isinstance(ast_node, str):
            return ast_node
        elif isinstance(ast_node, ngproc_parser.DlrExpr):
            func_name = ast_node.func_name
            if func_name == 'dijadmt_def':
                return conf.get_def(ast_eval(ast_node.args[0]))
            elif func_name == 'dijadmt_if':
                var_name = ast_eval(ast_node.args[0])
                value_true = ast_eval(ast_node.args[1])
                content = ast_eval(ast_node.args[2])
                if conf.get_def(var_name) == value_true:
                    return content
                else:
                    return ''
            else:
                raise NgProcEvalError(f'Unrecognized NgProc function {func_name}')
        else:
            raise NgProcEvalError(f'Unrecognized AST node type {type(ast_node)}')
    with path_in.open('r') as f_in:
        ngproc_parser.debug_ngproc = common_options.debug_ngproc
        ngproc_ast = ngproc_parser.parse(f_in.read())
        print(f'{ngproc_ast=}')
    processor_result = ast_eval(ngproc_ast)
    with path_working.open('w') as f_working:
        f_working.write(processor_result)

process_dict = {
    'none': process_none,
    'defsubs': process_defsubs,
    'ngproc': process_ngproc
}
