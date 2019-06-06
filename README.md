# Information
This repository is based on *Evaluating the Security of Logic Encryption Algorithms, HOST 2015*, whose source code is available at https://bitbucket.org/spramod/host15-logic-encryption/src/default/. We test the four types of single-fault models where exactly 1 gate is camouflaged: nand->nor, nor->nand, xor->xnor, xnor->xor on the rnd_c880 benchmarks.

# Download
To clone this repository, use the following command.

`$ git clone https://github.com/Alwaysenchanted/camouflaged_logc_single_fault.git`

# Environment
These codes should be run on Ubuntu 64-bit Linux. Python3 is also needed.

# Run
First, make sure that you have already download the "host15-logic-encryption" repository from https://bitbucket.org/spramod/host15-logic-encryption/src/default/. Then, use the three python3 scripts in the src directory to run the test and get the result.

### makeFault.py
This script will automatically create a folder in your directory of the "host15-logic-encryption" repository which includes four folders for four degrees of c880_enc encryption, namely 5%, 15%, 20% and 50%. Each of these folders contains four sub-folders corresponding to the four types of single-fault models. Benchmarks with single fault will be generated and placed in these sub-folders. 

### runSld.py
This script runs the "sld" binary in the "host15-logic-encryption" repository for each of the single-fault benchmarks generated in the last step. If the result is not UNSAT, the key information will be written to "result.txt" located in the same directory of the benchmarks.

### runLcmp.py
This script runs the "lcmp" binary in the "host15-logic-encryption" repository for the single-fault benchmarks and keys generated in the last two steps. The output of the script would be in the form of: name: different/total, where "name" refers to the fault type, "different" refers to the number of benchmarks which return "different", "total" refers to the total number of benchmarks of this fault type.



