import os
import sys
import pymake
import subprocess
import pathlib as pl


def get_ostag() -> str:
    """Determine operating system tag from sys.platform."""
    if sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform.startswith("win"):
        return "win64"
    elif sys.platform.startswith("darwin"):
        return "mac"
    raise ValueError(f"platform {sys.platform!r} not supported")


def get_cctag() -> str:
    """Determine operating system tag from sys.platform."""
    if sys.platform.startswith("linux"):
        return "icc"
    elif sys.platform.startswith("win"):
        return "icl"
    elif sys.platform.startswith("darwin"):
        return "icc"
    raise ValueError(f"platform {sys.platform!r} not supported")


if __name__ == "__main__":
    path = (
        pl.Path(os.path.dirname(pymake.__file__)) / "../"
    ).resolve() / "examples/buildall.py"

    cmds = [
        "python",
        path,
        f"--appdir={get_ostag()}",
        "-fc=ifort",
        f"-cc={get_cctag()}",
        f"--zip={get_ostag()}.zip",
        "--keep",
    ]

    retries = 3
    for idx in range(retries):
        p = subprocess.run(cmds)
        if p.returncode == 0:
            break
        print(f"run {idx + 1}/{retries} failed...rerunning")
