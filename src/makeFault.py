import os

dirs = ['c880_enc05', 'c880_enc10', 'c880_enc25', 'c880_enc50']
faults = ['nandtonor', 'nortonand', 'xortoxnor', 'xnortoxor']

base_dir = input("Input the absolute directory of \'host15-logic-encryption\': ").rstrip('/')
for dir in dirs:
    real_dir = base_dir + '/benchmarks/rnd_camouflaged_singefault/' + dir
    os.popen('mkdir -p ' + real_dir)
    for fault in faults:
        os.popen('mkdir -p ' + real_dir+'/'+fault)

for dir in dirs:
    file = open(base_dir + '/benchmarks/rnd/' + dir +'.bench')
    content = file.readlines()
    file.close()
    for fault in faults:
        real_dir = base_dir + '/benchmarks/rnd_camouflaged_singefault/' + dir + '/' + fault
        origin = fault[:fault.find('to')]
        target = fault[fault.find('to')+2:]
        count = 1
        for line in range(0, len(content)):
            if content[line].find(origin) > 0:
                if fault.find(('nortonand')) >= 0 and content[line].find('xnor') >= 0:
                    continue
                content[line] = content[line].replace(origin, target)
                f_temp = open(real_dir+'/'+dir+'_'+fault+'_'+str(count)+'.bench', 'w')
                f_temp.write(''.join(content))
                content[line] = content[line].replace(target, origin)
                count += 1



