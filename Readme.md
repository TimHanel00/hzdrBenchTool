## Small Repository Providing a data storing and vizualization Tool for the Alpaka Research Group (https://github.com/alpaka-group/alpaka)
### for manual local use:
	chmod +x ./bin/bench_store
	./bin/bench_store --args	
	chmod +x ./bin/bench_viz
	./bin/bench_viz --args
### install:
	chmod +x ./install
	./install
will add both skripts to your ~/.bashrc and make them executable \
you can now use bench_store and bench_viz from the command line \
### How to use it
#### Storing data into .json files:
	bench_store $dir1 ... $dirN --output-dir $pathToYourOutputDir
note that --output-dir is optional, otherwise the .json will be dumped at the current working directory \
Files should be of the format: $tag_$nr. \ 
Where Tag is a optional specifier to group data sets and nr is the number of elements used (X-axis argument). \
The $nr is necessary whereas files without $tag will be marked with the unspecified tag. Not using a _ will also mark them as unspecified. 
#### Visualizing created .json files: bench_viz <json_file> --byTag $tag OR --byAcc $substringOfAccelerator OR --byKernel $kernel_name
substrings for tag, accelerator or kernelName are also allowed (if its not ambigious)
##### example:
	bench_viz $pathTo/local_float.json --byAcc cpus 
will make plots for a the specified Accelerator CpuSerial for every Kernel and Tag
	bench_viz $pathTo/local_float.json --byKernel dot
will make plots for a the dotKernel for every Accelerator and Tag
	bench_viz $pathTo/local_float.json --byTag hal
will make plots for a the specified Tag: hal, for every Kernel and Accelerator
