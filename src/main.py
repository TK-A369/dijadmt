import argparse
import pathlib
import os

import conf_reader
import renderer
import managed_files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', action='store', nargs=1)
    parse_result = parser.parse_args()
    # parser.print_help()
    # print(parse_result)

    conf_root_path = parse_result.root[0]
    conf = conf_reader.Conf.read(conf_root_path)
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
        renderer.render_group(conf, g, managed_new_list, dir_working)

    managed_deleted_list = list(set(managed_old_list) - set(managed_new_list))
    if len(managed_deleted_list) > 0:
        print(f"The following files were managed but are to be deleted: {', '.join(managed_deleted_list)}")
        for mp in managed_deleted_list:
            os.unlink(mp)
    else:
        print("There are no previously managed files to be deleted")

    managed_files.save_managed_files(conf_root_path, managed_new_list)

if __name__ == "__main__":
    main()
