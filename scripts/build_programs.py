import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

from modflow_devtools.ostags import get_modflow_ostag

DEFAULT_RETRIES = 3
DPRECISION_EXES = ["mf2005", "mflgr", "mfnwt", "mfusg"]


def get_fc() -> str:
    """Determine Intel Fortran compiler to use based on the current platform."""
    return "ifort"


def get_cc() -> str:
    """Determine Intel C compiler to use based on the current platform."""
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
            Build MODFLOW-related executables, shared libraries and metadata files with pymake.
            """
        ),
    )
    parser.add_argument(
        "-k",
        "--keep",
        action=argparse.BooleanOptionalAction,
        help="Whether to keep (not recreate) existing binaries",
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        default=get_modflow_ostag(),
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
    keep = bool(args.keep)
    path = Path(args.path)
    path.mkdir(parents=True, exist_ok=True)
    zip_path = Path(path).with_suffix(".zip")
    dp_exes = ",".join(DPRECISION_EXES)
    retries = args.retries
    fc = get_fc()
    cc = get_cc()

    assert run_cmd(
        [
            "make-program",
            ":",
            "--appdir",
            path,
            "-fc",
            fc,
            "-cc",
            cc,
            "--zip",
            f"{path}.zip",
        ]
        + (["--keep"] if keep else [])
    ), "could not build default precision binaries"
    assert run_cmd(
        [
            "make-program",
            dp_exes,
            "--appdir",
            path,
            "--double",
            "--keep",
            "-fc",
            fc,
            "-cc",
            cc,
            "--zip",
            str(zip_path),
        ]
    ), f"could not build double precision binaries: {dp_exes}"
    assert run_cmd(
        [
            "make-code-json",
            "-ad",
            str(path),
            "--verbose",
        ]
    ), "could not make code.json"
    assert zip_path.is_file(), "could not build distribution zipfile"
    print(f"created distribution zipfile: {zip_path}")
