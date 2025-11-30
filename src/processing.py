import pathlib
import typing
import shutil

def process_none(path_in: pathlib.Path, path_working: pathlib.Path):
    # path_in.copy(path_working)
    shutil.copy(path_in, path_working)

process_dict = {
    'none': process_none
}
