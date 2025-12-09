import pathlib
import typing
import shutil
import re
import os

from . import conf_reader
from . import ngproc_parser

def process_none(path_in: pathlib.Path, path_working: pathlib.Path, conf: conf_reader.Conf):
    # path_in.copy(path_working)
    # shutil.copy(path_in, path_working)
    os.symlink(path_in, path_working)

def process_defsubs(path_in: pathlib.Path, path_working: pathlib.Path, conf: conf_reader.Conf):
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

# New Generation Processor
def process_ngproc(path_in: pathlib.Path, path_working: pathlib.Path, conf: conf_reader.Conf):
    with path_in.open('r') as f_in:
        ngproc_ast = ngproc_parser.parse(f_in.read())
        print(f'{ngproc_ast=}')

process_dict = {
    'none': process_none,
    'defsubs': process_defsubs,
    'ngproc': process_ngproc
}
