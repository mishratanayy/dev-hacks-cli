import os
import logging
import platform
import csv
import re
from collections import defaultdict
import subprocess

INPUT_DIR = os.getenv("SCHRODINGER_PERFORMANCE_TEST_INPUT")
OUTPUT_DIR = os.path.join(os.getenv("SCHRODINGER"), "performance_logs")


def get_input_files():
    input_files = []
    logging.info("Getting input files inside directory: " + INPUT_DIR)
    for files in os.listdir(INPUT_DIR):
        if files.endswith(".mae") or files.endswith(
                ".maegz") or files.endswith(".mae.gz"):
            input_files.append(os.path.join(INPUT_DIR, files))
    return input_files


def prepare_cmd_string(input_files):
    cmd_string = ""
    for file in input_files:
        cmd_string += "projectclose\n"
        cmd_string += f"entryimport {file}\n"
    cmd_string += "quit confirm=no\n"
    cmd_string += "quit"
    return cmd_string


def run_maestro(cmd_string):
    maestro_executable = os.path.join(os.getenv("SCHRODINGER", None),
                                      "maestro")
    args = []
    if platform.system() == "Darwin":
        args.append("-console")
    elif platform.system() == "Linux":
        args.append("-SGL")
    temp_file = "cmd_file.cmd"
    with open(temp_file, "w") as f:
        f.write(cmd_string)
    args.append("-c")
    args.append(os.path.join(os.getcwd(), temp_file))
    logging.info(f"Running {maestro_executable} {args}")
    subprocess.run([maestro_executable] + args)
    logging.info("Maestro run completed")
    os.remove(temp_file)
    logging.info("Removing temporary file")


def process_files_in_directory(directory_path, output_csv):
    # Dictionary to hold the data, with filenames as keys
    data = defaultdict(dict)
    all_functions = set()

    # Iterate through each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".log"):
            file_path = os.path.join(directory_path, filename)
            logging.info(f"Processing file: {file_path}")
            with open(file_path, 'r') as file:
                lines = file.readlines()

                file_name = lines[0].strip().strip('"')
                for line in lines[1:]:
                    match = re.match(r"(\w+)\s*=\s*(\d+)\s*ms", line.strip())
                    if match:
                        function_name = match.group(1)
                        value = int(match.group(2))
                        data[file_name][function_name] = value
                        all_functions.add(function_name)

    # Convert the collected data into a CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['Filename'] + sorted(all_functions)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for file_name, functions in data.items():
            row = {'Filename': file_name}
            for function in all_functions:
                row[function] = functions.get(function, "")
            writer.writerow(row)

    print(f"CSV file '{output_csv}' created successfully.")


def perform_cleanup(directory):
    logging.info("Performing cleanup in directory: " + directory)
    if os.path.exists(directory):
        for file in os.listdir(directory):
            os.remove(os.path.join(directory, file))
    logging.info("Cleanup done")


def main():
    perform_cleanup(OUTPUT_DIR)
    input_files = get_input_files()
    logging.info(f"input_files: {input_files}")
    cmd_string = prepare_cmd_string(input_files)
    run_maestro(cmd_string)
    process_files_in_directory(OUTPUT_DIR,
                               os.path.join(OUTPUT_DIR, "output_metrics.csv"))


def verify_setup():
    env_vars = ("SCHRODINGER", "SCHRODINGER_PERFORMANCE_TEST_INPUT")
    for var in env_vars:
        if not os.getenv(var, None):
            logging.error(f"Environment variable {var} is not set")
            exit(1)
    logging.info("Environment variables : OK")
    print("SCHRODINGER:", os.getenv("SCHRODINGER", None))
    print("SCHRODINGER_PERFORMANCE_TEST_INPUT:",
          os.getenv("SCHRODINGER_PERFORMANCE_TEST_INPUT", None))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting performance tests")
    verify_setup()
    main()
