#!/usr/bin/python

import argparse
import pathlib
import os

from . import conf_reader
from . import renderer
from . import managed_files
from . import cli_parsing

__version__ = '0.1.0'

def main():
    (parser, parse_result, cli_common_options) = cli_parsing.parse()
    # parser.print_help()
    # print(parse_result)

    conf_root_path = parse_result.root[0]
    conf = conf_reader.Conf.read(conf_root_path, parse_result.defs or {})
    # print(conf)

    managed_old_list = managed_files.read_managed_files(conf_root_path)

    enabled_groups = conf.enable.copy()
    i = 0
    while i < len(enabled_groups):
        conf.get_group(enabled_groups[i]).resolve_deps(enabled_groups)
        i += 1
    print(f"Enabled groups: {', '.join(enabled_groups)}")

    managed_new_list = []
    dir_working = pathlib.Path("./working").resolve()
    for gn in enabled_groups:
        g = conf.get_group(gn)
        renderer.render_group(conf, g, managed_old_list, managed_new_list, dir_working, cli_common_options)

    managed_deleted_list = list(set(managed_old_list) - set(managed_new_list))
    if len(managed_deleted_list) > 0:
        print(f"The following files were managed but are to be deleted: {', '.join(managed_deleted_list)}")
        if not cli_common_options.dry_run:
            for mp in managed_deleted_list:
                os.unlink(mp)
    else:
        print("There are no previously managed files to be deleted")

    if not cli_common_options.dry_run:
        managed_files.save_managed_files(conf_root_path, managed_new_list)

if __name__ == "__main__":
    main()
