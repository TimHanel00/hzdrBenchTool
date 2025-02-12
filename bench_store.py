#!/usr/bin/env python3
import os
import re
import sys
import json
import time
from datetime import datetime

def custom_error():
    message="Usage: bench_store <directory> <prefixTag1> ... <prefixTag2> \n--output-dir <optional argument for The json target directory output directory, Default: current working directory>"
    sys.stderr.write(f"{message}\n")
    sys.exit(2)
def custom_file_error():
    message="files in the target directory have to contain a number to specify the nr_of_Elements \n general format should be $tag_$nrElems"
    sys.stderr.write(f"{message}\n")
    sys.exit(2)
def load_filenames(directories):
    ret=[]
    for directory in directories:
        if not os.path.isdir(directory):
            print(f"Error: The directory '{directory}' does not exist.")
            custom_error()
            return []
        filenames_print=[f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        filenames=[(directory,f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        print(f'at dir: {directory} found {filenames_print}\n')
        ret.extend(filenames)
    return ret

def extract_accelerator_types(file_path):
    # Extract all AcceleratorTypes from the file content
    accelerator_types = set()
    with open(file_path, 'r') as file:
        content = file.readlines()

    for line in content:
        if line.startswith('AcceleratorType'):
            match = re.match(r"AcceleratorType:(\S+)", line)
            if match:
                accelerator_types.add(match.group(1))
    
    return list(accelerator_types)

def extract_kernel_data(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()

    all_kernel_data = {}

    # Regex pattern to capture AcceleratorType and kernel names with bandwidths
    accelerator_pattern = re.compile(r"AcceleratorType:(\S+)")
    kernel_pattern = re.compile(r"(\S+Kernel)\s+(\d+\.\d+)")

    current_accelerator = None
    kernel_data = {}

    for line in content:
        # Match AcceleratorType in the file
        accel_match = accelerator_pattern.search(line)
        if accel_match:
            if current_accelerator and kernel_data:
                # If we have previous accelerator data, store it
                if current_accelerator not in all_kernel_data:
                    all_kernel_data[current_accelerator]=[]
                all_kernel_data[current_accelerator].append(kernel_data)
            
            # Start a new section for the current AcceleratorType
            current_accelerator = accel_match.group(1)
            kernel_data = {}

        # Match kernel data in the line
        kernel_match = kernel_pattern.search(line)
        if kernel_match and current_accelerator:
            kernel_name = kernel_match.group(1)
            bandwidth = float(kernel_match.group(2))  # Convert bandwidth to float
            kernel_data[kernel_name] = bandwidth
    #add last data
    if current_accelerator and kernel_data:
        if current_accelerator not in all_kernel_data:
                    all_kernel_data[current_accelerator]=[]
        all_kernel_data[current_accelerator].append(kernel_data)

    return all_kernel_data
def extractInnerData(dest,source,accelerator_type,prefix_number):
    if accelerator_type not in dest:
        dest[accelerator_type] = {}

    for kernel in source.keys():

        if kernel not in dest[accelerator_type]:
            dest[accelerator_type][kernel] = {}
            dest[accelerator_type][kernel]["nr_of_elements"] = []
            dest[accelerator_type][kernel]["bandwidth"] = []

        # Check if the data already exists for the same accelerator and kernel
        dest[accelerator_type][kernel]["nr_of_elements"].append(prefix_number)
        dest[accelerator_type][kernel]["bandwidth"].append(source[kernel])
def main():
    ##manual argument parsing since I couldnt get costum error msg to work in argparse 
    if len(sys.argv) < 3:
        custom_error()

    # Parse arguments
    directories = sys.argv[1:]

    output_dir = None  # Default to None, which means current directory
    if '--output-dir' in sys.argv:
        output_dir_index = sys.argv.index('--output-dir') + 1

    # Extract the output directory value
        if output_dir_index < len(sys.argv):
            output_dir = sys.argv[output_dir_index]
        else:
            custom_error("Error: '--output-dir' option requires a directory path.")
        
        # Filter out '--output-dir' and its associated directory value from the prefixes list
        directories = [pref for idx, pref in enumerate(directories) if pref != "--output-dir" and idx != output_dir_index-1]
# Load filenames matching the prefixes
    filenames = load_filenames(directories)

    if len(filenames)==0:
        print("No matching files found.")
        return

    # Dictionary to store final data for JSON
    float_data = {}
    double_data={}
    # Process each prefix and its corresponding files
    for directory,file in filenames:
        # Regular expression to match the desired format (prefix followed by an underscore, a number, and optional * characters)
        match = re.search(rf"([a-zA-Z]*)(_?)(\d+)\*?", file)
        number=0
        prefix=""
        if match:
            # If the file contains a number
            number_str = match.group(3) 
            number = int(number_str) if number_str.isdigit() else float(number_str)
            # Check if there's a prefix before the number
            prefix = match.group(1) if match.group(1) and match.group(2) else "unspecified"
        else:
            # If the file does not contain a number, raise an error
            custom_file_error()
        if prefix not in float_data:
            float_data[prefix]={}
        if prefix not in double_data:
            double_data[prefix]={}
        # Extract the number from the filename (e.g., cuda_24.txt -> 24)

        file_path = os.path.join(directory, file)

        # Extract Accelerator Types from the file
        accelerator_types = extract_accelerator_types(file_path)

        if not accelerator_types:
            continue  # Skip files if no accelerator types are found

        # Extract kernel data from the file
        #kernel_data = extract_kernel_data(file_path)
        # Add data for each AcceleratorType found in the file
        for accelerator_type, kernel_dataS in extract_kernel_data(file_path).items():
            float_Kernel_data=kernel_dataS[0]
            double_Kernel_data=kernel_dataS[1]
            extractInnerData(float_data[prefix],float_Kernel_data,accelerator_type,number)
            extractInnerData(double_data[prefix],double_Kernel_data,accelerator_type,number)
                   


    # Generate a timestamped filename
    current_timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    base_filename = f"benchData_{current_timestamp}"

    # Ensure the output directory is valid
    if output_dir:
        if not os.path.isdir(output_dir):
            custom_error(f"Error: The specified output directory '{output_dir}' does not exist.")
        output_path_float = os.path.join(output_dir, f"{base_filename}_float.json")
        output_path_double = os.path.join(output_dir, f"{base_filename}_double.json")
    else:
        output_path_float = os.path.join(os.getcwd(), f"{base_filename}_float.json")
        output_path_double = os.path.join(os.getcwd(), f"{base_filename}_double.json")

    # Save JSON files
    with open(output_path_float, "w") as json_file:
        json.dump(float_data, json_file, indent=4)

    with open(output_path_double, "w") as json_file:
        json.dump(double_data, json_file, indent=4)

    # Print the absolute paths of the generated JSON files
    print(f"Data has been successfully extracted and written to:\n"
        f" - {os.path.abspath(output_path_float)}\n"
        f" - {os.path.abspath(output_path_double)}")


if __name__ == "__main__":
    main()
