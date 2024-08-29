import os
import logging
import platform
import csv
import re
import sys
from collections import defaultdict
import subprocess
import glob
import shutil

INPUT_DIR = os.getenv("SCHRODINGER_PERFORMANCE_TEST_INPUT")
OUTPUT_DIR = os.getenv("SCHRODINGER_PERFORMANCE_TEST_OUTPUT")


def get_csv_name_by_os(name):
    name += "_" + sys.platform.lower()
    name += ".csv"
    return name


SUPPORTED_EXTENSIONS = (".mae", ".maegz", ".mae.gz", ".sd", ".sdf", ".pdb")


def get_input_files():
    input_files = []
    logging.info("Getting input files inside directory: " + INPUT_DIR)
    for files in os.listdir(INPUT_DIR):
        if files.endswith(SUPPORTED_EXTENSIONS):
            input_files.append(os.path.join(INPUT_DIR, files))
    logging.info(f"Input files found: {input_files}")
    return input_files


def prepare_cmd_string(input_files):
    cmd_string = ""
    for file in input_files:
        output_log_file = os.path.join(OUTPUT_DIR,
                                       os.path.basename(file) + ".log")
        cmd_string += "projectclose\n"
        cmd_string += f"entryimport {file} wsreplace=false wsinclude=none\n"
        cmd_string += f"timingsetup file={output_log_file}\n"
        cmd_string += "timingstart\n"
        cmd_string += "entrywsinclude all\n"
        cmd_string += "timingstop\n"
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
    logging.info("Command file created", temp_file)
    args.append("-c")
    args.append(os.path.join(os.getcwd(), temp_file))
    logging.info(f"Running {maestro_executable} {args}")
    subprocess.run([maestro_executable] + args)
    logging.info("Maestro run completed")
    os.remove(temp_file)
    logging.info("Removing temporary command file")


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
                        if data[file_name].get(function_name) is None:
                            data[file_name][function_name] = 0
                        data[file_name][function_name] += value
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

    logging.info(f"CSV file '{output_csv}' created successfully.")


def perform_cleanup(directory):
    logging.info("Performing cleanup in directory: " + directory)

    shutil.rmtree(directory, ignore_errors=True)
    os.makedirs(directory)
    logging.info("Cleanup completed.")


def write_graphics_output_to_csv(input_files, output_file):
    """
    Parses multiple input files to create a structured CSV with activities as headers and their corresponding 'Time (s)' values.
    
    Args:
        input_files (list of tuples): A list where each tuple contains the path to the input text file and the associated filename.
        output_file (str): The path to the output CSV file.
    """
    activities = [
        "Main Drawing", "Onscreen Drawing", "Drawing Setup",
        "Structure Drawing", "Python Drawing", "Overlay Drawing",
        "Command Handling", "Regenerate DGOs", "Regenerate main CT"
    ]

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        # Write the header row once
        writer.writerow(["Filename"] + activities)

        for input_file, filename in input_files:
            # Initialize a dictionary to hold Time (s) values for each activity
            activity_times = {activity: "000.000" for activity in activities}

            with open(input_file, 'r') as infile:
                lines = infile.readlines()

                for line in lines:
                    clean_line = line.strip().replace('"', '').strip()
                    if clean_line and not clean_line.startswith(
                            "Timing") and not clean_line.startswith("Period"):
                        parts = clean_line.split('\t')
                        if len(parts) >= 2:
                            activity = parts[0].strip()
                            time_value = parts[1].strip().replace(
                                "\t", "")  # Remove additional tabs
                            if activity in activity_times:
                                activity_times[activity] = time_value

            # Write the row with the filename and activity times
            writer.writerow(
                [filename] +
                [activity_times[activity] for activity in activities])


def process_graphics_output_in_directory(directory, output_file):
    logging.info("Processing graphics output in directory: " + directory)
    input_files = glob.glob(os.path.join(directory, "*.log"))
    input_data = []
    for file in input_files:
        input_data.append((file, os.path.basename(file).split(".")[0]))
    write_graphics_output_to_csv(input_data, output_file)
    logging.info("Graphics output processed successfully at : " + output_file)


def main():
    perform_cleanup(OUTPUT_DIR)
    input_files = get_input_files()
    logging.info(f"input_files: {input_files}")
    cmd_string = prepare_cmd_string(input_files)
    run_maestro(cmd_string)
    process_files_in_directory(
        os.path.join(OUTPUT_DIR, "performance_logs"),
        os.path.join(OUTPUT_DIR,
                     get_csv_name_by_os("output_command_performance")))
    process_graphics_output_in_directory(
        OUTPUT_DIR,
        os.path.join(OUTPUT_DIR,
                     get_csv_name_by_os("output_graphics_performance")))


def verify_setup():
    env_vars = ("SCHRODINGER", "SCHRODINGER_PERFORMANCE_TEST_INPUT",
                "SCHRODINGER_PERFORMANCE_TEST_OUTPUT")
    for var in env_vars:
        if not os.getenv(var, None):
            logging.error(f"Environment variable {var} is not set")
            exit(1)
    logging.info("Environment variables : OK")
    print("SCHRODINGER:", os.getenv("SCHRODINGER", None))
    print("SCHRODINGER_PERFORMANCE_TEST_INPUT:",
          os.getenv("SCHRODINGER_PERFORMANCE_TEST_INPUT", None))
    print("SCHRODINGER_PERFORMANCE_TEST_OUTPUT:",
          os.getenv("SCHRODINGER_PERFORMANCE_TEST_OUTPUT", None))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting performance tests")
    verify_setup()
    main()
