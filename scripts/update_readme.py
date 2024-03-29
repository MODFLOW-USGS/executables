import pathlib as pl

proj_root = pl.Path(__file__).parent.parent
target_file = pl.Path("code.md")
TAG = "| Program | Version | UTC Date |"
FILES = ("code.json", "code.md")


def _update_readme() -> None:
    with open(proj_root / "README.md", "r") as f:
        readme_md = f.read().splitlines()
    with open("code.md", "r") as f:
        code_md = f.read().splitlines()
    with open(proj_root / "README.md", "w") as f:
        for line in readme_md:
            if TAG not in line:
                f.write(f"{line}\n")
            else:
                for code_line in code_md:
                    f.write(f"{code_line}\n")
                break


if __name__ == "__main__":
    _update_readme()
