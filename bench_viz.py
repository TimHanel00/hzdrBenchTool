#!/usr/bin/env python3
import json
import sys
import matplotlib.pyplot as plt
import math
def extractData(data):
    x=0.0
    y=0.0
    for key,val in data.items():
        if isinstance(val, int):
            x=val
        else:
            y=val
    return x,y
def byKernel(data, kernel_name):
    # Ensure that the requested kernel exists in the data
    tag_set = set()
    
    kernel_set = set()  # Use a set to store unique kernel names

    for accelerators_data in data.values():  # Iterate over tag values
        for kernels_data in accelerators_data.values():  # Iterate over accelerator values
            kernel_set.update(kernels_data.keys())  # Add all kernel names to the set
    kernel_name=find_matching_key(kernel_name,kernel_set,"Kernel")
    accelerators=set()
    for tag, accelerators_data in data.items():
        for accelerator, kernels_data in accelerators_data.items():
            if kernel_name in kernels_data:
                accelerators.add(accelerator)
                tag_set.add(tag)

    if not tag_set:
        print(f"Error: No data found for kernel '{kernel_name}'")
        return

    num_tags = len(accelerators)
    num_rows = math.ceil(num_tags / 3)
    num_cols = 3  # Maximum 3 subplots per row

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 5))  # Adjust figsize as needed
    axes = axes.flatten()  # Flatten to easily index the subplots

    # Create a subplot for each tag (the x-axis will represent the accelerators)
    for idx,accel in enumerate(accelerators):
        print(idx)
        ax = axes[idx]
        ax.set_title(f'{accel}')
        ax.set_xlabel('nr_of_elements')
        ax.set_ylabel('Bandwidth (GB/s)')
        for tag in tag_set:
            if accel in data[tag]:

                kernels_data=data[tag][accel]
                if kernel_name in kernels_data:
                    nr_of_elements = kernels_data[kernel_name]['nr_of_elements']
                    bandwidth = kernels_data[kernel_name]['bandwidth']
                    ax.plot(nr_of_elements, bandwidth, label=f'{tag}')

        ax.legend()

    # Turn off any unused subplots
    for i in range(num_tags, len(axes)):
        axes[i].axis('off')

    fig.suptitle(f'Benchmark visualization for Kernel: {kernel_name}')
    plt.tight_layout()
    plt.show()
# Function to generate plots by tag (e.g., cuda, hip)
def plot_(data):
    # Ensure that we have data for the requested tag
    accelerators=set()
    for tag in data.keys():
        accelerators.update(data[tag].keys())

    num_accelerators = len(accelerators)

    # Calculate grid dimensions: 3 subplots per row
    num_rows = math.ceil(num_accelerators / 3)
    num_cols = 3  # Maximum 3 subplots per row

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 5))  # Adjust figsize as needed
    axes = axes.flatten()  # Flatten to easily index the subplots

    # Create a subplot for each accelerator (e.g., 'CpuSerial', 'CpuOmpBlocks')
    for idx, accelerator_type in enumerate(accelerators):
        ax = axes[idx]
        ax.set_title(f'{accelerator_type}')
        ax.set_xlabel('Number of Elements')
        ax.set_ylabel('Bandwidth (GB/s)')
        kernelData={}
        for tag in data.keys():
            kernels_list = data[tag][accelerator_type]
            xs=set()
            ys={}
            # Loop through the list of kernel data
            for kernel_name,val in kernels_list.items():
                if kernel_name not in kernelData:
                    kernelData[kernel_name]=[]
                if len(kernelData[kernel_name])<1:
                    kernelData[kernel_name].append(val['nr_of_elements'])
                elif len(kernelData[kernel_name])<2:   
                    kernelData[kernel_name].append(val['bandwidth'])
                else:
                    kernelData[kernel_name][0].extend(val['nr_of_elements'])
                    kernelData[kernel_name][1].extend(val['bandwidth'])
        for key in kernelData.keys():
            ax.scatter(kernelData[key][0], kernelData[key][1], label=f"{key}")
        ax.legend()

    # Turn off any unused subplots
    for i in range(num_accelerators, len(axes)):
        axes[i].axis('off')
    fig.suptitle(f'Benchmark visualization for DataSet')
    plt.tight_layout()
    plt.show()


# Function to generate plots by accelerator (e.g., CpuSerial, CpuOmpBlocks) showing tags
def byAccelerator(data, accelerator_type):
    accels=set()
    for tag, accelerators_data in data.items():
            accels.update(accelerators_data.keys())
    accelerator_type=find_matching_key(accelerator_type,accels,"Accelerators")
    # Ensure that the requested accelerator exists in the data
    tag_set = set()
    for tag, accelerators_data in data.items():
        if accelerator_type in accelerators_data:
            tag_set.add(tag)
    if not tag_set:
        print(f"Error: No data found for accelerator '{accelerator_type}'")
        return

    kernels_list = list(data[next(iter(tag_set))][accelerator_type].keys())
    num_kernels = len(kernels_list)
    num_rows = math.ceil(num_kernels / 3)
    num_cols = 3  # Maximum 3 subplots per row

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 5))  # Adjust figsize as needed
    axes = axes.flatten()  # Flatten to easily index the subplots

    # Create a subplot for each kernel (the x-axis will represent the tags)
    for idx, kernel_name in enumerate(kernels_list):
        ax = axes[idx]
        ax.set_title(f'{kernel_name}')
        ax.set_xlabel('nr_of_elements')
        ax.set_ylabel('Bandwidth (GB/s)')
        # Collect the data for the specified accelerator across different tags
        for tag in tag_set:
            if accelerator_type in data[tag]:
                kernel_data = data[tag][accelerator_type]
                if kernel_name in kernel_data:
                    nr_of_elements = kernel_data[kernel_name]['nr_of_elements']
                    bandwidth = kernel_data[kernel_name]['bandwidth']
                    ax.plot(nr_of_elements, bandwidth, label=f'{tag}')

        ax.legend()

    # Turn off any unused subplots
    for i in range(num_kernels, len(axes)):
        axes[i].axis('off')

    fig.suptitle(f'Benchmark visualization for Accelerator: {accelerator_type}')
    plt.tight_layout()
    plt.show()
def plot_by_tag(data, tag):
    tag=find_matching_key(tag,data.keys(),"Tags")
    # Ensure that we have data for the requested tag
    if tag not in data:
        
        print(f"Error: No data found for tag '{tag}'")
        return
    
    accelerators = list(data[tag].keys())

    num_accelerators = len(accelerators)

    # Calculate grid dimensions: 3 subplots per row
    num_rows = math.ceil(num_accelerators / 3)
    num_cols = 3  # Maximum 3 subplots per row

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 5))  # Adjust figsize as needed
    axes = axes.flatten()  # Flatten to easily index the subplots

    # Create a subplot for each accelerator (e.g., 'CpuSerial', 'CpuOmpBlocks')
    for idx, accelerator_type in enumerate(accelerators):
        ax = axes[idx]
        ax.set_title(f'{accelerator_type}')
        ax.set_xlabel('Number of Elements')
        ax.set_ylabel('Bandwidth (GB/s)')
        kernels_list = data[tag][accelerator_type]
        xs=set()
        ys={}
        # Loop through the list of kernel data
        for kernel_name,val in kernels_list.items():
            x,y=val['nr_of_elements'],val['bandwidth']
            ax.plot(x, y, label=f"{kernel_name}")
        ax.legend()

    # Turn off any unused subplots
    for i in range(num_accelerators, len(axes)):
        axes[i].axis('off')
    fig.suptitle(f'Benchmark visualization for Tag: {tag}')
    plt.tight_layout()
    plt.show()

# Ensure you import your plotting functions here
# from your_script import plot_by_tag, byAccelerator, byKernel
def find_matching_key(substring, available_keys, category_name):
    """
    Find a matching key from available_keys based on the given substring.
    
    - If exactly one match is found, return it.
    - If multiple matches are found, raise an error highlighting the ambiguity.
    - If no matches are found, raise an error indicating the substring is invalid.
    """
    matches = [key for key in available_keys if substring.lower() in key.lower()]
    
    if len(matches) == 1:
        return matches[0]  # Return the unique match
    elif len(matches) > 1:
        print(f"Error: Ambiguous {category_name} '{substring}'. Possible matches: {matches}")
        sys.exit(1)
    else:
        print(f"Error: No matching {category_name} found for '{substring}'. Available options: {available_keys}")
        sys.exit(1)
def main():
    # Check if there are enough arguments
    if len(sys.argv) < 2:
        print("Invalid arguments. Usage: bench_viz <json_file> --byTag $tag OR --byAcc $substringOfAccelerator OR --byKernel $kernel_name")
        sys.exit(1)

    # Parse the json file
    json_file = sys.argv[1]
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract the command (either --byTag, --byAcc, or --byKernel)
    if len(sys.argv) < 3:
        print("Warning! No selection specified, plotting scatterPlot across All data")
        print("Usage hint: python script.py <json_file> --byTag $tag OR --byAcc $acc OR --byKernel $kernel_name")
        plot_(data)
        return 
    command = sys.argv[2]

    if command == '--byTag' and len(sys.argv) == 4:
        tag = sys.argv[3]
        plot_by_tag(data, tag)  # Call the plot_by_tag function with the given tag
    elif command == '--byAcc' and len(sys.argv) == 4:
        substring = sys.argv[3]
        byAccelerator(data, substring)  # Call the byAccelerator function with the given accelerator substring
    elif command == '--byKernel' and len(sys.argv) == 4:
        kernel_name = sys.argv[3]
        byKernel(data, kernel_name)  # Call the byKernel function with the given kernel name
    else:
        plot_(data)
        print("Usage hint: python script.py <json_file> --byTag $tag OR --byAcc $acc OR --byKernel $kernel_name")
        #sys.exit(1)

if __name__ == '__main__':
    main()

    

