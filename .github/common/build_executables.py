import sys
import subprocess

RETRIES = 3


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


def mfpymake_run_command(args) -> bool:
    success = False
    for idx in range(RETRIES):
        p = subprocess.run(args)
        if p.returncode == 0:
            success = True
            break
        print(f"{args[0]} run {idx + 1}/{RETRIES} failed...rerunning")
    return success


if __name__ == "__main__":
    cmd = [
        "make-program",
        ":",
        f"--appdir={get_ostag()}",
        "-fc=ifort",
        f"-cc={get_cctag()}",
        f"--zip={get_ostag()}.zip",
        "--keep",
    ]

    if not mfpymake_run_command(cmd):
        raise RuntimeError("could not build the executables")

    cmd = [
        "make-code-json",
        "-f",
        f"code.json",
        "--verbose",
    ]

    if not mfpymake_run_command(cmd):
        raise RuntimeError(f"could not run {cmd[0]}")
