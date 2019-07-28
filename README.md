# Information
This repository is based on *Evaluating the Security of Logic Encryption Algorithms, HOST 2015*, whose source code is available at https://bitbucket.org/spramod/host15-logic-encryption/src/default/. We test the four types of single-fault models where exactly 1 gate is camouflaged: nand->nor, nor->nand, xor->xnor, xnor->xor on the rnd_c880 benchmarks.

# Download
To clone this repository, use the following command.

`$ git clone https://github.com/Alwaysenchanted/camouflaged_logc_single_fault.git`

# Environment
These codes should be run on Ubuntu 64-bit Linux. Python3 is also needed.

# Run
First, make sure that you have already download the "host15-logic-encryption" repository from https://bitbucket.org/spramod/host15-logic-encryption/src/default/. Then, use the python3 script in the src directory to run the test and get the result.

### test_single_fault.py
Before running the script, the fault types and benchmarks should be defined in the script. For example:

`faults = ['nortoxnor']
`bench = 'c880'
`dirs = [bench+'_enc05']

These mean the script will run nor-to-xnor single-fault test on c880_enc05.bench. Besides, the variable base_dir should be assigned the path to the directory 'host15-logic-encryption'.


