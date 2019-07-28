import os

#All the types of faults to be tested
faults = ['nortoxnor']#['nandtonor','nortonand','xortoxnor','xnortoxor','xortonor', 'xortonand', 'xnortonor', 'xnortonand', 'nortoxor', 'nandtoxor', 'nortoxnor', 'nandtoxnor']
bench = 'c880'
dirs = [bench+'_enc05']#[bench+'_enc25', bench+'_enc50']  All the benches to be tested
encrypt_type = 'rnd'

base_dir ='path to /host15-logic-encryption' #The directory of the HOST-15 code

sld = base_dir + '/bin/sld '
lcmp = base_dir + '/bin/lcmp'
os.popen('mkdir -p '+base_dir+'/benchmarks/'+encrypt_type+'_camouflaged_singefault')

lcmp_result = []  #The result of lcmp

for dir in dirs:
    real_dir = base_dir + '/benchmarks/'+encrypt_type+'_camouflaged_singefault'+'/' + dir
    os.popen('mkdir -p ' + real_dir)
    for fault in faults:
        os.popen('mkdir -p ' + real_dir + '/' + fault)
    file = open(base_dir + '/benchmarks/'+ encrypt_type +'/' + dir +'.bench')
    content = file.readlines()
    file.close()
    for fault in faults:
        real_dir = base_dir + '/benchmarks/'+encrypt_type+'_camouflaged_singefault'+'/' + dir + '/' + fault
        origin = fault[:fault.find('to')]
        target = fault[fault.find('to') + 2:]
        count = 1
        result = []
        tmp_lcmp_result = []
        for line in range(0, len(content)):
            if content[line].find(origin) > 0:
                #To eliminate the case of mixing nor with xnor
                if fault.find('norto') >= 0 and fault.find('xnorto') < 0 and content[line].find('xnor') >= 0:
                    continue
                content[line] = content[line].replace(origin, target)
                f_temp = open(real_dir + '/' + dir + '_' + fault + '_' + str(count) + '.bench', 'w')
                f_temp.write(''.join(content))
                f_temp.close()
                content[line] = content[line].replace(target, origin)
                command = sld+real_dir+'/'+dir+'_'+fault+'_'+str(count)+'.bench '+base_dir+'/benchmarks/original/'+dir[:dir.find('_')]+'.bench'
                output = os.popen(command).read().strip('\n')
                info = output[output.find('key='): output.find('iteration=') - 1]
                if len(info) > 0:
                    result.append('i=' + str(count) + ' ' + info.strip('\n'))
                    if info.find('=x') < 0:
                        command = lcmp + ' ' + base_dir + '/benchmarks/original/' + dir[:dir.find(
                            '_')] + '.bench ' + real_dir + '/' + dir + '_' + fault + '_' + str(count) + '.bench ' + info.strip('\n')[info.find('key='):]
                        tmp_lcmp_result.append(os.popen(command).read())
                        # if(tmp_lcmp_result[-1].find('equivalent') >= 0):   #Used to find the equivalent cases
                        #     gate_name = content[line][:content[line].find('=')].strip()
                        #     print(gate_name)
                os.popen('rm '+real_dir + '/' + dir + '_' + fault + '_' + str(count) + '.bench')
                count += 1
        file = open(real_dir + '/result.txt', 'w')
        file.write('\n'.join(result))
        file.close()
        lcmp_result.append(dir+'_'+fault+': ' + str(sum([1 for line in tmp_lcmp_result if line.find('different') >= 0]))+'/'+str(len(tmp_lcmp_result)))
        file = open(base_dir + '/benchmarks/'+encrypt_type+'_camouflaged_singefault/lcmp_result_'+bench+'_'+fault.txt', 'w')
        file.write('\n'.join(lcmp_result))
        file.close()
