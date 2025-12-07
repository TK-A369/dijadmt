import typing
import pathlib
import pickle

def read_managed_files(conf_root_path) -> typing.List[pathlib.Path]:
    managed_path = pathlib.Path(conf_root_path).parent / 'managed.pickle'
    if managed_path.exists():
        with managed_path.open('rb') as f_managed:
            managed_list = pickle.load(f_managed)
        return managed_list
    else:
        print("Old managed files list not found")
        return []

def save_managed_files(conf_root_path, managed_list):
    managed_path = pathlib.Path(conf_root_path).parent / 'managed.pickle'
    with managed_path.open('wb') as f_managed:
        pickle.dump(managed_list, f_managed)
