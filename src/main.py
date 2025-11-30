import argparse

import conf_reader

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', action='store', nargs=1)
    parse_result = parser.parse_args()
    # parser.print_help()
    print(parse_result)

    conf = conf_reader.Conf.read(parse_result.root[0])
    print(conf)

if __name__ == "__main__":
    main()
