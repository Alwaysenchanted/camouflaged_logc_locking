import os
import random
import sys
import monosat

base_dir = '/home/tanqinhan/Desktop/CamouflagedLogic/host15-logic-encryption'   #directory of HOST-15 code
SMT_dir = '/home/tanqinhan/Desktop/CamouflagedLogic/SMTAttack'     #directory of SMTAttack
gates = ['nand', 'nor', 'xor', 'xnor']
sat_tck = 'python3 '+SMT_dir+'/src/main.py sat_tck '
ddip_tck = 'python3 '+SMT_dir+'/src/main.py ddip_tck  '

args = sys.argv
bench_type = args[1]
bench_name = args[2]
encs = args[3].split(',')
fault_num = int(args[4])
attack_type = args[5]
benches = [bench_name+'_enc'+enc for enc in encs]#['apex2', 'apex4', 'c432', 'c499', 'c880', 'c1355', 'c1908', 'c2670', 'c3540', 'c5315', 'c7552', 'dalu', 'des', 'ex5', 'ex1010', 'i4', 'i7', 'i8', 'i9', 'k2', 'seq']
os.popen('mkdir -p '+base_dir+'/benchmarks/'+bench_type+'_multi_faults/')
all_result = []
for bench in benches:
    # print(bench)
    gate_map = dict()
    file = open(base_dir+'/benchmarks/'+bench_type+'/'+bench+'.bench', 'r')
    content = file.readlines()
    old_content = [l for l in content]
    file.close()
    # print(content)
    for line in range(len(content)):
        if content[line].find(('(')) < 0 or content[line].find((')')) < 0:
            continue
        args = content[line][content[line].find('(') + 1: content[line].find(')')].split(',')
        if len(args) > 2:
            continue
        if content[line].find('nand') >= 0:
            gate_map[line] = 'nand'
        elif content[line].find('xor') >= 0:
            gate_map[line] = 'xor'
        elif content[line].find('xnor') >= 0:
            gate_map[line] = 'xnor'
        elif content[line].find('nor') >= 0:
            gate_map[line] = 'nor'

    if len(gate_map.keys()) < fault_num:
         continue

    success = False
    count = 1
    result = ''
    while(not success):
        print('Iteration:', count)
        count += 1

        content = [l for l in old_content]
        keys = list(gate_map.keys())
        for i in range(fault_num):
            index = random.randint(0, len(keys)-1)
            gate_index = keys[index]
            keys.pop(index)
            ori_gate = gate_map[gate_index]
            new_gate = [gat for gat in gates if gat != ori_gate][random.randint(0, 2)]
            content[gate_index] = content[gate_index].replace(ori_gate, new_gate)
        file = open(base_dir+'/benchmarks/'+bench_type+'_multi_faults/'+bench+'_faulty.bench', 'w')
        file.write(''.join(content))
        file.close()
        if attack_type == 'sat':
            result = os.popen(sat_tck+base_dir+'/benchmarks/'+bench_type+'_multi_faults/'+bench+'_faulty.bench '+base_dir+'/benchmarks/original/'+bench_name+'.bench').read()
        elif attack_type == 'ddip':
            result = os.popen(ddip_tck+base_dir+'/benchmarks/'+bench_type+'_multi_faults/'+bench+'_faulty.bench '+base_dir+'/benchmarks/original/'+bench_name+'.bench').read()
        else:
            print('Wrong attack type!')
            exit(0)
        if result.find('ERROR') >= 0 or count >= 10:
            success = True
            all_result.append(bench+' ERROR')
            print(result)
            print(bench, 'ERROR')
        result = result[result.find('Last SAT Call'):]
        if result.find('UNSAT') >= 0:
            success = True
            all_result.append(bench + ' UNSAT')
            print(bench, 'UNSAT')
#file = open('./result.txt', 'w')
#file.write('\n'.join(all_result))
#file.close()

