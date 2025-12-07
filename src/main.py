import argparse
import pathlib

import conf_reader
import renderer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', action='store', nargs=1)
    parse_result = parser.parse_args()
    # parser.print_help()
    print(parse_result)

    conf = conf_reader.Conf.read(parse_result.root[0])
    print(conf)

    enabled_groups = conf.enable.copy()
    i = 0
    while i < len(enabled_groups):
        conf.get_group(enabled_groups[i]).resolve_deps(enabled_groups)
        i += 1
    print(f"Enabled groups: {', '.join(enabled_groups)}")

    dir_working = pathlib.Path("./working").resolve()
    for gn in enabled_groups:
        g = conf.get_group(gn)
        renderer.render_group(conf, g, dir_working)

if __name__ == "__main__":
    main()
