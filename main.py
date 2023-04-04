import contextlib
import glob
import os
import subprocess
from argparse import ArgumentParser

SCHRODINGER = os.getenv("SCHRODINGER")
SCHRODINGER_SRC = os.getenv("SCHRODINGER_SRC")
MAESTRO_SRC = "maestro-src"
MMSHARE = "mmshare"
REPOS = [MMSHARE, MAESTRO_SRC]
CLANG_CMD = ["clang-format", "--style=file", "-i"]
YAPF_CMD = ["yapf", "-i"]
FLAKE_CMD = ["flake8"]
BUILD_TYPE = os.getenv("BUILD_TYPE")
WAFBUILD = f"waf configure build install --build={BUILD_TYPE}"
MMSHARE_SRC_PATH = os.path.join(SCHRODINGER_SRC, MMSHARE)
MAESTRO_SRC_PATH = os.path.join(SCHRODINGER_SRC, MAESTRO_SRC)


def _verify_environment():
    if not SCHRODINGER:
        raise RuntimeError("$SCHRODINGER not defined")
    if not SCHRODINGER_SRC:
        raise RuntimeError("$SCHRODINGER_SRC not defined")
    if not BUILD_TYPE or BUILD_TYPE not in ['debug', 'optimzed']:
        raise RuntimeError(
            "$BUILD_TYPE not defined, it should be set to 'debug' or 'optimized'"
        )


@contextlib.contextmanager
def cd_dir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


def get_mmshare_build_dir():
    mmshare_build_exp = os.path.join(SCHRODINGER, "mmshare-v*")
    path = glob.glob(mmshare_build_exp)
    if len(path) == 0:
        raise ValueError("No mmshare build found")
    return path[0]


def _get_repo_path(repo):
    return os.path.join(SCHRODINGER_SRC, repo)


def _is_valid_repo(repo):
    full_path = os.path.join(SCHRODINGER_SRC, repo)
    return os.path.isdir(full_path) and repo in REPOS


def _get_modified_files(repo, diff_generator):
    if not _is_valid_repo(repo):
        raise ValueError(f"Invalid repo: {repo}")
    with cd_dir(_get_repo_path(repo)):
        git_command = f"git diff --name-only {diff_generator}"
        output = subprocess.check_output(git_command.split())
        return output.decode("utf-8").strip().split("\n")


def _is_clang_supported(file):
    cpp_extensions = [".cpp", ".h", ".cxx", ".c", ".hpp"]
    return any(file.endswith(extension) for extension in cpp_extensions)


def _is_yapf_supported(file):
    return file.endswith(".py") or file.endswith("wscript")


def format_files_from_repo(repo, diff_generator="HEAD"):
    modified_files = _get_modified_files(repo, diff_generator=diff_generator)
    yapf_supported_files = [
        file for file in modified_files if _is_yapf_supported(file)
    ]
    clang_supported_files = [
        file for file in modified_files if _is_clang_supported(file)
    ]
    with cd_dir(_get_repo_path(repo)):
        if yapf_supported_files:
            yapf_command = YAPF_CMD + yapf_supported_files
            subprocess.call(yapf_command)
            flake_command = FLAKE_CMD + yapf_supported_files
            subprocess.call(flake_command)
        if clang_supported_files:
            clang_command = CLANG_CMD + clang_supported_files
            subprocess.call(clang_command)


def build_mmshare_python():
    mmshare_build_dir = get_mmshare_build_dir()
    python_build_dir = os.path.join(mmshare_build_dir, "python")
    make_install = "make install"
    with cd_dir(python_build_dir):
        subprocess.call(make_install.split())
    python_test_dir = os.path.join(mmshare_build_dir, "python", "test")
    with cd_dir(python_test_dir):
        subprocess.call(make_install.split())


def build_maestro_without_test():
    with cd_dir(MAESTRO_SRC_PATH):
        build_cmd = WAFBUILD + " --target=maestro"
        subprocess.call(build_cmd, env=os.environ, shell=True)


def build_mmshare_without_make():
    with cd_dir(MMSHARE_SRC_PATH):
        build_cmd = WAFBUILD + " --skipmakesteps"
        subprocess.call(build_cmd, env=os.environ, shell=True)


def __main__():
    parser = ArgumentParser(
        prog="best_script.py",
        description="This provides basic hacks that you can perform to "
        "speed up "
        "your mmshare and maestro-src development time",
        add_help=True)
    parser.add_argument(
        "-f",
        "--format",
        help="Format the modified files, you should pass the repo first "
        "and then diff generator string for example "
        "[-f maestro-src \"HEAD~1 HEAD\"]",
        nargs=2)
    parser.add_argument("--build-maestro-only",
                        help="Build maestro without building tests",
                        action="store_true",
                        default=False)
    parser.add_argument("--build-mmshare-python",
                        help="Build mmshare python modules and test without "
                        "actually building whole mmshare",
                        action="store_true",
                        default=False)
    parser.add_argument("--build-mmshare-without-make",
                        help="Build mmshare without makesteps",
                        action="store_true",
                        default=False)
    args = parser.parse_args()
    if args.format:
        format_files_from_repo(repo=args.format[0],
                               diff_generator=args.format[1])

    if args.build_mmshare_python:
        build_mmshare_python()

    if args.build_mmshare_without_make:
        build_mmshare_without_make()

    if args.build_maestro_only:
        build_maestro_without_test()


if __name__ == '__main__':
    _verify_environment()
    __main__()
