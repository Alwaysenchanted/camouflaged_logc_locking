import os

dirs = ['c880_enc05', 'c880_enc10', 'c880_enc25', 'c880_enc50']
faults = ['nandtonor', 'nortonand', 'xortoxnor', 'xnortoxor']

base_dir = input("Input the absolute directory of \'host15-logic-encryption\': ").rstrip('/')
lcmp = base_dir + '/bin/lcmp'
total_result = dict()

for dir in dirs:
    for fault in faults:
        real_dir = base_dir+'/benchmarks/rnd_camouflaged_singefault/'+dir+'/'+fault
        file = open(real_dir + '/result.txt', 'r')
        content = file.readlines()
        file.close()
        result = []
        for line in content:
            line = line.strip('\n')
            index = line[2: line.find(' key=')]
            if line.find('=x') < 0:
                command = lcmp+' '+base_dir+'/benchmarks/original/c880.bench '+real_dir+'/'+dir+'_'+fault+'_'+index+'.bench '+line[line.find('key='):]
                result.append('i='+str(index)+' '+os.popen(command).read())
        total_result[dir+'_'+fault] = str(sum([1 for line in result if line.find('different') > 0]))+'/'+str(len(result))

for key in total_result.keys():
    print(key + ': ' + total_result[key])
