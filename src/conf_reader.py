import tomllib
import pathlib
import dataclasses
import typing

@dataclasses.dataclass(init=False)
class Group:
    name: str
    in_path: str
    process: str

    def __init__(self, name, group_dict):
        self.name = name
        self.in_path = group_dict['in_path']
        self.process = group_dict.get('process', 'none')

@dataclasses.dataclass(init=False)
class Conf:
    src_path: str
    groups: typing.Dict[str, typing.Type[Group]]
    subconfs: typing.List['Conf']

    def __init__(self, src_path, groups, subconfs):
        self.src_path = src_path
        self.groups = groups
        self.subconfs = subconfs

    @staticmethod
    def read(path):
        path_obj = pathlib.Path(path).resolve()
        with path_obj.open('rb') as f:
            file_dict = tomllib.load(f)

        groups = dict()
        for name, g in file_dict.get('groups', {}).items():
            groups[name] = Group(name, g)

        subconfs = []
        for subconf_path in file_dict.get('subconfs', []):
            subpath = str(pathlib.Path(path_obj.parent, subconf_path).resolve())
            print(f"Reading subconfig at {subpath}")
            subconf = Conf.read(subpath)
            subconfs.append(subconf)

        return Conf(str(path_obj), groups, subconfs)
