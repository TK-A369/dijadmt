import tomllib
import pathlib
import dataclasses
import typing

class ConflictingGroupsError(Exception):
    def __init__(self, g1, g2):
        self.g1 = g1
        self.g2 = g2

    def __str__(self):
        return f"Group {self.g1} is conflicting with {self.g2}"

@dataclasses.dataclass(init=False)
class Group:
    name: str
    in_path: str
    process: str
    requires: typing.List[str]
    conflicts: typing.List[str]

    def __init__(self, name, group_dict):
        self.name = name
        self.in_path = group_dict['in_path']
        self.process = group_dict.get('process', 'none')
        self.requires = group_dict.get('requires', [])
        self.conflicts = group_dict.get('conflicts', [])

    def resolve_deps(self, deps_list):
        for g in self.conflicts:
            if g in deps_list:
                raise ConflictingGroupsError(self.name, g)

        for g in self.requires:
            if g not in deps_list:
                deps_list.append(g)

@dataclasses.dataclass(init=False)
class Conf:
    src_path: str
    groups: typing.Dict[str, typing.Type[Group]]
    subconfs: typing.List['Conf']
    enable: typing.List[str]

    def __init__(self, src_path, groups, subconfs, enable):
        self.src_path = src_path
        self.groups = groups
        self.subconfs = subconfs
        self.enable = enable

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

        return Conf(str(path_obj), groups, subconfs, file_dict.get('enable', []))

    def get_group(self, group_name) -> typing.Optional[typing.Type[Group]]:
        if group_name in self.groups:
            return self.groups[group_name]
        else:
            for sc in self.subconfs:
                res = sc.get_group(group_name)
                if res is not None:
                    return res
            return None
