import pathlib
import typing
import random
import shutil
import os

from . import conf_reader
from . import processing
from . import cli_parsing

class FileExistsUnmanagedError(Exception):
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return f"File {self.file_path} is the new configuration artifact, but it already exists on the filesystem"

def render_file(
        in_file_path: pathlib.Path,
        path_working: pathlib.Path,
        conf: conf_reader.Conf,
        group: conf_reader.Group,
        managed_old_list: typing.List[str],
        managed_new_list: typing.List[str],
        common_options: cli_parsing.CliCommonOptions):
    print(f"Running processor {group.process} on {in_file_path} into {path_working}")
    processing.process_dict[group.process](in_file_path, path_working, conf, common_options)

    symlink_path = group.out_path / in_file_path.relative_to(group.in_path)
    if str(symlink_path) not in managed_old_list and symlink_path.exists():
        raise FileExistsUnmanagedError(str(symlink_path))
    if not common_options.dry_run:
        symlink_path.parent.mkdir(parents=True, exist_ok=True)
        symlink_path.unlink(missing_ok=True)
    managed_new_list.append(str(symlink_path))
    if common_options.use_symlinks:
        print(f"Creating symlink {symlink_path} -> {path_working}")
        if not common_options.dry_run:
            os.symlink(path_working, symlink_path)
    else:
        print(f"Copying {path_working} to {symlink_path}")
        if not common_options.dry_run:
            shutil.copy(path_working, symlink_path)

def render_group(
        conf: conf_reader.Conf,
        group: conf_reader.Group,
        managed_old_list: typing.List[str],
        managed_new_list: typing.List[str],
        dir_working: pathlib.Path,
        common_options: cli_parsing.CliCommonOptions):
    dir_working_group = dir_working / group.name
    dir_working_group.mkdir(parents=True, exist_ok=True)
    in_path_obj = pathlib.Path(group.in_path)
    if in_path_obj.is_dir():
        for (dir_path, dirs, files) in in_path_obj.walk(follow_symlinks=True):
            for fn in files:
                path_working = dir_working_group / f"{fn}_{random.randint(0, 9999) :0>4}"
                render_file(dir_path / fn, path_working, conf, group, managed_old_list, managed_new_list, common_options)
    elif in_path_obj.is_file():
        path_working = dir_working_group / f"{in_path_obj.name}_{random.randint(0, 9999) :0>4}"
        render_file(in_path_obj, path_working, conf, group, managed_old_list, managed_new_list, common_options)
    else:
        print(f"Warning: path {in_path_obj} does not exist")
