from typing import List, Hashable, Dict


def assert_keys_exist(keys: List[Hashable], dictionary: Dict):
    for key in keys:
        assert key in dictionary, f"Missing key {key} in {dictionary}."
