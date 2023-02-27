import argparse
import sys
import subprocess
import textwrap
from pathlib import Path

DEFAULT_RETRIES = 3


def get_ostag() -> str:
    """Determine operating system tag from sys.platform."""
    if sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform.startswith("win"):
        return "win64"
    elif sys.platform.startswith("darwin"):
        return "mac"
    raise ValueError(f"platform {sys.platform!r} not supported")


def get_cc() -> str:
    """Determine operating system tag from sys.platform."""
    if sys.platform.startswith("linux"):
        return "icc"
    elif sys.platform.startswith("win"):
        return "icl"
    elif sys.platform.startswith("darwin"):
        return "icc"
    raise ValueError(f"platform {sys.platform!r} not supported")


def run_cmd(args) -> bool:
    success = False
    for idx in range(DEFAULT_RETRIES):
        p = subprocess.run(args)
        if p.returncode == 0:
            success = True
            break
        print(f"{args[0]} run {idx + 1}/{DEFAULT_RETRIES} failed...rerunning")
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=f"Build MODFLOW-related binaries and metadata files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Build MODFLOW-releated executables, shared libraries and metadata files with pymake.
            """
        ),
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        default=get_ostag(),
        help="Path to create built binaries and metadata files",
    )
    parser.add_argument(
        "-r",
        "--retries",
        type=int,
        required=False,
        default=DEFAULT_RETRIES,
        help="Number of times to retry a failed build",

    )
    args = parser.parse_args()

    # output path
    path = Path(args.path)
    path.mkdir(parents=True, exist_ok=True)

    # number of retries
    retries = args.retries

    # C compiler
    cc = get_cc()

    # create code.json
    if not run_cmd([
        "make-code-json",
        "-f",
        str(path / "code.json"),
        "--verbose",
    ]):
        raise RuntimeError(f"could not make code.json")

    # build binaries
    if not run_cmd([
        "make-program", ":",
        f"--appdir={path}",
        "-fc=ifort", f"-cc={cc}",
        f"--zip={path}.zip",
        "--keep",
    ]):
        raise RuntimeError("could not build binaries")
