import pathlib
import typing
import shutil
import re
import os

import conf_reader

def process_none(path_in: pathlib.Path, path_working: pathlib.Path, conf: conf_reader.Conf):
    # path_in.copy(path_working)
    # shutil.copy(path_in, path_working)
    os.symlink(path_in, path_working)

def process_defsubs(path_in: pathlib.Path, path_working: pathlib.Path, conf: conf_reader.Conf):
    with path_in.open('r') as f_in, path_working.open('w') as f_working:
        s_in = f_in.read()
        s_subs = re.sub(
            r'\$dijadmt_if{([a-zA-Z0-9_]+)}{([^{}]*)}{([^{}]*)}',
            lambda m: m.group(3) if conf.get_def(m.group(1)) == m.group(2) else "",
            s_in)
        s_subs = re.sub(
            r'\$dijadmt_def{([a-zA-Z0-9_]+)}',
            lambda m: conf.get_def(m.group(1)),
            s_subs)
        s_subs = re.sub(
            r'\$dijadmt_escape{(.)}',
            lambda m: conf.get_def(m.group(1)),
            s_subs)
        f_working.write(s_subs)

process_dict = {
    'none': process_none,
    'defsubs': process_defsubs
}
