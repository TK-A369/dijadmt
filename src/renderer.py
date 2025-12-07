import pathlib
import typing
import random
import shutil
import os

import conf_reader
import processing

def render_file(
        in_file_path: pathlib.Path,
        path_working: pathlib.Path,
        conf: conf_reader.Conf,
        group: conf_reader.Group,
        use_symlinks: bool):
    print(f"Running processor {group.process} on {in_file_path} into {path_working}")
    processing.process_dict[group.process](in_file_path, path_working, conf)

    symlink_path = group.out_path / in_file_path.relative_to(group.in_path)
    symlink_path.parent.mkdir(parents=True, exist_ok=True)
    symlink_path.unlink(missing_ok=True)
    if use_symlinks:
        print(f"Creating symlink {symlink_path} -> {path_working}")
        os.symlink(path_working, symlink_path)
    else:
        print(f"Copying {symlink_path} -> {path_working}")
        shutil.copy(path_working, symlink_path)

def render_group(
        conf: conf_reader.Conf,
        group: conf_reader.Group,
        dir_working,
        use_symlinks=True):
    dir_working_group = dir_working / group.name
    dir_working_group.mkdir(parents=True, exist_ok=True)
    in_path_obj = pathlib.Path(group.in_path)
    if in_path_obj.is_dir():
        for (dir_path, dirs, files) in in_path_obj.walk(follow_symlinks=True):
            for fn in files:
                path_working = dir_working_group / f"{fn}_{random.randint(0, 9999) :0>4}"
                render_file(dir_path / fn, path_working, conf, group, use_symlinks)
    elif in_path_obj.is_file():
        path_working = dir_working_group / f"{in_path_obj.name}_{random.randint(0, 9999) :0>4}"
        render_file(in_path_obj, path_working, conf, group, use_symlinks)
    else:
        print(f"Warning: path {in_path_obj} does not exist")
