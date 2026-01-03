import os
from pathlib import Path


def get_app_base_dir() -> str:
    return os.path.join(Path.home(), "DFTFlow")


def get_runs_base_dir() -> str:
    return os.path.join(get_app_base_dir(), "runs")
