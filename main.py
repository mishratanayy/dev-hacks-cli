import os
import subprocess
from argparse import ArgumentParser
import logging
import contextlib
import glob

SCHRODINGER = os.getenv("SCHRODINGER")
SCHRODINGER_SRC = os.getenv("SCHRODINGER_SRC")
MAESTRO_SRC = "mmshare/maestro"
MMSHARE = "mmshare"
REPOS = [MMSHARE, MAESTRO_SRC]
BUILD_TYPE = os.getenv("BUILD_TYPE")

CLANG_CMD = ["clang-format", "--style=file", "-i"]
YAPF_CMD = ["yapf", "-i"]
FLAKE_CMD = ["flake8"]
WAF_CMD = f"waf configure build install --build={BUILD_TYPE}"

MMSHARE_SRC_PATH = os.path.join(SCHRODINGER_SRC, MMSHARE)
MAESTRO_SRC_PATH = os.path.join(SCHRODINGER_SRC, MAESTRO_SRC)
GIT_PULL_CMD = "git pull --rebase --autostash"
SCRIPT_DIR = os.path.dirname(__file__)
PYTEST_CMD = os.path.join(SCHRODINGER, "utilities", "py.test")


def run_cmd(cmd, cwd=os.getcwd()):
    try:
        logging.info(f"Command: {cmd} , inside directory: {cwd}")
        output = subprocess.run(cmd, cwd=cwd , capture_output=True)
        if stderr:= output.stderr:
            print("--------------------")
            logging.error(str(stderr))
            print("--------------------")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command {cmd} failed with error {e}")


class EnvironmentVerifier:
    def __init__(self):
        self._env_vars = [
            "SCHRODINGER", "SCHRODINGER_SRC", "BUILD_TYPE", "SCHRODINGER_LIB"
        ]

    def verify(self, print_values=False):
        missing_env_vars = [
            env for env in self._env_vars if env not in os.environ
        ]
        for env in self._env_vars:
            if env in os.environ and print_values:
                print(f"{env} = {os.environ[env]}")
        if len(missing_env_vars):
            raise ValueError(
                f"Environment variables {missing_env_vars} is not set")


class CodeFormatter:
    def formatFiles(self, repo=MMSHARE, diff_generator="HEAD"):
        modified_files = self._getModifiedFiles(repo, diff_generator)

        yapf_supported_files = [
            file for file in modified_files
            if self._isYapfSupported(file) and os.path.isfile(file)
        ]
        clang_supported_files = [
            file for file in modified_files
            if self._isClangSupported(file) and os.path.isfile(file)
        ]
        self._formatPythonFiles(yapf_supported_files)
        self._formatCppFiles(clang_supported_files)
    
    def _formatPythonFiles(self, files):

        if files:
            run_cmd(YAPF_CMD + files)
            run_cmd(FLAKE_CMD + files)
        else: 
            logging.info("No python files to format")
    
    def _formatCppFiles(self, files):
        if files:
            run_cmd(CLANG_CMD + files)
        else:
            logging.info("No cpp files to format")

    def _getModifiedFiles(self, repo, diff_generator):
        if not _is_valid_repo(repo):
            raise ValueError(f"Invalid repo: {repo}")

        with cd_dir(_get_repo_path(repo)):
            git_command = f"git diff --name-only {diff_generator}"
            output = subprocess.check_output(git_command.split())
            return output.decode("utf-8").strip().split("\n")

    def _isClangSupported(self, file):
        cpp_extensions = [".cpp", ".h", ".cxx", ".c", ".hpp"]
        return any(file.endswith(extension) for extension in cpp_extensions)

    def _isYapfSupported(self, file):
        return file.endswith(".py") or file.endswith("wscript")


class Builder:
    def buildMaestroWithoutTests(self):
        cmd = WAF_CMD + ' --target=maestro'
        run_cmd(cmd, cwd=MAESTRO_SRC_PATH)

    def buildMMSharePython(self):
        mmshare_build_dir = self._get_mmshare_build_dir()
        make_py = ["make","python"]
        run_cmd(make_py, cwd=mmshare_build_dir)
        logger.info("Done!")

    def buildMMShareWithoutMakeSteps(self):
        cmd = WAF_CMD + ' --skipmakesteps'
        run_cmd(cmd, cwd=MMSHARE_SRC_PATH)

    def _get_mmshare_build_dir(self):
        return glob.glob(os.path.join(SCHRODINGER, "mmshare-v*"))[0]


class Tester:
    def run_tests(self, test_path, count):
        count = int(count)
        if count < 1:
            raise ValueError("Count should be greater than 0")

        output_file = os.path.join(SCHRODINGER, "test_output.log")
        if os.path.exists(output_file):
            os.remove(output_file)

        logging.info(f"Running tests in parallel {test_path} , {count} times")

        if os.path.exists(test_path):
            test_run_cmd = [PYTEST_CMD, "-n", "auto", test_path]
            logging.info(f"Writing results to {output_file}")

            with open(output_file, "w") as f:
                f.write(f"Test output for : {test_path} \n")
                f.write(f"Test ran for {count} times")

                for i in range(count):
                    if subprocess.call(test_run_cmd, stdout=f, stderr=f) != 0:
                        logging.error(
                            "Test failed in one of the runs, stopping further executions"
                        )
                        return

            logging.info("Test ran successfully every time")


def _get_repo_path(repo):
    return os.path.join(SCHRODINGER_SRC, repo)


def _is_valid_repo(repo):
    full_path = _get_repo_path(repo)
    return os.path.isdir(full_path) and repo in REPOS


@contextlib.contextmanager
def cd_dir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)


def parse_args():
    parser = ArgumentParser(
        prog="best_script.py",
        description="This provides basic hacks that you can perform to "
        "speed up "
        "your mmshare and maestro-src development time",
        add_help=True)

    parser.add_argument("--verify-env",
                        help="Verify the environment variables",
                        action="store_true")

    parser.add_argument("--format",
                        help="Format the modified files",
                        nargs=1,
                        metavar=("diff_generator"))

    parser.add_argument("--build-maestro-only",
                        help="Build maestro without building tests",
                        action="store_true")

    parser.add_argument("--build-mmshare-python",
                        help="Build mmshare python modules and test without "
                        "actually building the whole mmshare",
                        action="store_true")

    parser.add_argument("--build-mmshare-without-make",
                        help="Build mmshare without make steps",
                        action="store_true")

    parser.add_argument("--run-tests",
                        help="Run tests X number of times",
                        nargs=2,
                        metavar=("test_path", "count"))

    return parser.parse_args()


def __main__():
    args = parse_args()

    env_verifier = EnvironmentVerifier()
    env_verifier.verify(print_values=bool(args.verify_env))

    if args.format:
        code_formatter = CodeFormatter()
        code_formatter.formatFiles(diff_generator=args.format[0])

    if args.build_maestro_only:
        builder = Builder()
        builder.buildMaestroWithoutTests()

    if args.build_mmshare_python:
        builder = Builder()
        builder.buildMMSharePython()

    if args.build_mmshare_without_make:
        builder = Builder()
        builder.buildMMShareWithoutMakeSteps()


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
        __main__()
    except Exception as e:
        logging.error(e)
        exit(1)
