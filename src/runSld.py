import os

dirs = ['c880_enc05', 'c880_enc10', 'c880_enc25', 'c880_enc50']
faults = ['nandtonor', 'nortonand', 'xortoxnor', 'xnortoxor']

base_dir = input("Input the absolute directory of \'host15-logic-encryption\': ").rstrip('/')
sld = base_dir + '/bin/sld '


for dir in dirs:
    for fault in faults:
        real_dir = base_dir+'/benchmarks/rnd_camouflaged_singefault/'+dir+'/'+fault
        command = 'ls '+real_dir+'/'
        category = os.popen(command).readlines()
        result = []
        for line in range(0, len(category)):
            name = category[line]
            if name.find(".bench") >= 0:
                index = name[name.find(fault)+len(fault)+1: name.find(".bench")]
                command = sld+real_dir+'/'+dir+'_'+fault+'_'+index+'.bench '+base_dir+'/benchmarks/original/c880.bench'
                output = os.popen(command).read().strip('\n')
                info = output[output.find('key='): output.find('iteration=')-1]
                if len(info) > 0:
                    result.append('i='+index+' '+info.strip('\n'))
        file = open(real_dir + '/result.txt', 'w')
        file.write('\n'.join(result))




