#!/usr/bin/env python3
"""Download and install USGS MODFLOW executables.

This script requires Python 3.6 or later.
"""

import json
import os
import sys
import urllib
import urllib.request
import zipfile
from pathlib import Path

# See https://developer.github.com/v3/repos/releases/
owner = "MODFLOW-USGS"
repo = "executables"
api_url = f"https://api.github.com/repos/{owner}/{repo}"


exe_suffix = ""
if sys.platform.startswith("linux"):
    ostag = "linux"
    so_suffix = ".so"
elif sys.platform.startswith("win"):
    ostag = "win" + ("64" if sys.maxsize > 2**32 else "32")
    exe_suffix = ".exe"
    so_suffix = ".dll"
elif sys.platform.startswith("darwin"):
    ostag = "mac"
    so_suffix = ".dylib"
else:
    raise ValueError(f"platform {sys.platform!r} not supported")


def get_avail_releases():
    with urllib.request.urlopen(f"{api_url}/releases") as resp:
        result = resp.read()
    releases = json.loads(result.decode())
    avail_releases = [release["tag_name"] for release in releases]
    avail_releases.insert(0, "latest")
    return avail_releases


def download_and_extract(url, download_pth, bindir, force=False):
    if download_pth.is_file() and not force:
        print(
            f"using previous download '{download_pth}' "
            "(use --force to re-download)"
        )
    else:
        print(f"downloading to '{download_pth}'")
        urllib.request.urlretrieve(url, download_pth)
    print(f"extracting files to '{bindir}'")
    with zipfile.ZipFile(download_pth, "r") as zipf:
        zipf.extractall(bindir)
        return set(zipf.namelist())


def print_columns(items, line_chars=79):
    item_chars = max(len(item) for item in items)
    num_cols = line_chars // item_chars
    num_rows = len(items) // num_cols
    if len(items) % num_cols != 0:
        num_rows += 1
    for row_num in range(num_rows):
        row_items = items[row_num::num_rows]
        print(" ".join(item.ljust(item_chars) for item in row_items).rstrip())


def main(bindir, release_id="latest", force=False):
    if bindir == ":select":
        options = []
        # check if conda
        conda_bin = Path(sys.prefix) / "conda-meta" / ".." / "bin"
        if conda_bin.exists() and os.access(conda_bin, os.W_OK):
            options.append(conda_bin.resolve())
        home_local_bin = Path.home() / ".local" / "bin"
        if home_local_bin and os.access(home_local_bin, os.W_OK):
            options.append(home_local_bin)
        local_bin = Path("/usr") / "local" / "bin"
        if local_bin and os.access(local_bin, os.W_OK):
            options.append(local_bin)
        # any other possible locations?
        options_d = dict(enumerate(options, 1))
        print("select an extraction directory:")
        for iopt, opt in options_d.items():
            print(f"{iopt:2d}: {opt}")
        num_tries = 0
        while True:
            num_tries += 1
            res = input("> ")
            try:
                bindir = options_d[int(res)]
                break
            except (KeyError, ValueError):
                if num_tries < 3:
                    print("invalid option, try choosing option again")
                else:
                    raise RuntimeError("invalid option, too many attempts")

    bindir = Path(bindir).resolve()
    if not bindir.is_dir():
        raise OSError(f"extraction directory '{bindir}' does not exist")
    elif not os.access(bindir, os.W_OK):
        raise OSError(f"extraction directory '{bindir}' is not writable")

    if release_id == "latest":
        req_url = f"{api_url}/releases/latest"
    else:
        req_url = f"{api_url}/releases/tags/{release_id}"
    try:
        with urllib.request.urlopen(req_url) as resp:
            result = resp.read()
    except urllib.error.HTTPError as err:
        if err.code == 404:
            avail_releases = get_avail_releases()
            raise ValueError(
                f"Release {release_id!r} not found -- "
                f"choose from {avail_releases}"
            )
        else:
            raise err
    release = json.loads(result.decode())
    tag_name = release["tag_name"]
    print(f"fetched release {tag_name!r}")
    assets = release.get("assets", [])
    for asset in assets:
        if ostag in asset["name"]:
            break
    else:
        raise ValueError(
            f"could not find {ostag!r} from {tag_name!r}; "
            f"see available assets here: {release['html_url']}"
        )
    download_url = asset["browser_download_url"]
    src_fname = Path(asset["name"])
    # change local download name to use tag, so they are more unique
    dst_fname = f"{src_fname.stem}-{tag_name}{src_fname.suffix}"
    downloads_dir = Path.home() / "Downloads"
    if downloads_dir.is_dir() and os.access(downloads_dir, os.W_OK):
        files = download_and_extract(
            download_url, downloads_dir / dst_fname, bindir, force
        )
    else:
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdirname:
            files = download_and_extract(
                download_url, Path(tmpdirname) / dst_fname, bindir, force
            )

    # Check installation, set file mode, show listing
    do_chmod = ostag in ["linux", "mac"]
    items = []
    if "code.json" in files:
        code = json.loads((bindir / "code.json").read_text())
        files.remove("code.json")

        def append_item(key, pth):
            if not pth.is_file():
                print(f"file {pth} does not exist")
            else:
                items.append(f"{pth.name} ({code[key]['version']})")
                files.remove(pth.name)
            return

        for key in sorted(code):
            if code[key].get("shared_object"):
                pth = bindir / f"{key}{so_suffix}"
                append_item(key, pth)
            else:
                pth = bindir / f"{key}{exe_suffix}"
                append_item(key, pth)
                if do_chmod and pth.is_file():
                    pth.chmod(pth.stat().st_mode | 0o111)
                # check if double version exists
                pth = bindir / f"{key}dbl{exe_suffix}"
                if code[key].get("double_switch", True) and pth.is_file():
                    append_item(key, pth)
                    if do_chmod:
                        pth.chmod(pth.stat().st_mode | 0o111)
    else:  # release 1.0 did not have code.json
        for file in sorted(files):
            pth = bindir / file
            if not pth.is_file():
                print(f"file {pth} does not exist")
                continue
            items.append(file)
            if do_chmod and not file.endswith(so_suffix):
                pth.chmod(pth.stat().st_mode | 0o111)
        files = []

    print(f"installed {len(items)} executables:")
    print_columns(items)

    if files:
        print(f"unexpected remaining {len(files)} files:")
        print_columns(sorted(files))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "BINDIR",
        nargs=1,
        help="directory to extract executables; use ':select' to help choose",
    )
    parser.add_argument(
        "--release-id",
        default="latest",
        help="release_id (default: latest)",
    )
    parser.add_argument(
        "--force", action="store_true", help="force re-download"
    )
    args = vars(parser.parse_args())
    args["bindir"] = args.pop("BINDIR")[0]
    try:
        main(**args)
    except (OSError, RuntimeError, ValueError) as err:
        sys.exit(err)
