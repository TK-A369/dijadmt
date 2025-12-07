import tomllib
import pathlib
import dataclasses
import typing
import collections
import re

class ConflictingGroupsError(Exception):
    def __init__(self, g1, g2):
        self.g1 = g1
        self.g2 = g2

    def __str__(self):
        return f"Group {self.g1} is conflicting with {self.g2}"

def resolve_defs(s: str, get_def_fn: collections.abc.Callable[[str], str]) -> str:
    return re.sub(r'\${([a-zA-Z0-9_]+)}', lambda m: get_def_fn(m.group(1)), s)

@dataclasses.dataclass(init=False)
class Group:
    name: str
    in_path: pathlib.Path
    out_path: pathlib.Path
    process: str
    requires: typing.List[str]
    conflicts: typing.List[str]

    def __init__(self, name, group_dict, dir_obj, get_def_fn):
        self.name = name
        self.in_path = dir_obj / resolve_defs(group_dict['in_path'], get_def_fn)
        self.out_path = dir_obj / resolve_defs(group_dict['out_path'], get_def_fn)
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
    defs: typing.Dict[str, str]

    def __init__(self, src_path, groups, subconfs, enable, defs):
        self.src_path = src_path
        self.groups = groups
        self.subconfs = subconfs
        self.enable = enable
        self.defs = defs

    @staticmethod
    def read(path):
        path_obj = pathlib.Path(path).resolve()
        with path_obj.open('rb') as f:
            file_dict = tomllib.load(f)

        subconfs = []
        for subconf_path in file_dict.get('subconfs', []):
            subpath = str(pathlib.Path(path_obj.parent, subconf_path).resolve())
            print(f"Reading subconfig at {subpath}")
            subconf = Conf.read(subpath)
            subconfs.append(subconf)

        defs = file_dict.get('defs', {})

        groups = dict()
        conf = Conf(str(path_obj), groups, subconfs, file_dict.get('enable', []), defs)
        for name, g in file_dict.get('groups', {}).items():
            conf.groups[name] = Group(name, g, path_obj.parent, lambda dn: conf.get_def(dn))

        return conf

    def get_group(self, group_name) -> typing.Optional[typing.Type[Group]]:
        if group_name in self.groups:
            return self.groups[group_name]
        else:
            for sc in self.subconfs:
                res = sc.get_group(group_name)
                if res is not None:
                    return res
            return None

    def get_def(self, def_name) -> typing.Optional[str]:
        if def_name in self.defs:
            return self.defs[def_name]
        else:
            for sc in self.subconfs:
                res = sc.get_def(def_name)
                if res is not None:
                    return res
