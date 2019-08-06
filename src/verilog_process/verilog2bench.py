import re
import os
import sys

# This script cannot handle sub-module instantiation statements at present. It can only transform the gates in one-level modules into benches
class Gate:
    input_num = 0
    inputs = []
    output = ''
    type = ''

    def __init__(self, input_num, inputs, output, type):
        self.input_num = input_num
        self.inputs = [e for e in inputs]
        self.output = output
        self.type = type


verilog_file = sys.argv[1]
file = open(verilog_file, 'r')
verilog_text = file.read()
file.close()

pattern = re.compile('module.*?endmodule', re.S)  #Recognize the module definition
modules = pattern.findall(verilog_text)
module_names = [e[e.find('module ') + 7: e.find(' (')] for e in modules]
gate_names = ['and','or','nand','nor','xor','xnor','buf','not','AND2','AND3','AND4','BUF','CLKBUF','AOI211','AOI21','AOI221','AOI222','AOI22','DFF','FA','HA','INV','MUX2','NAND2','NAND3','NAND4','NOR2','NOR3','NOR4','OAI211','OAI21','OAI221','OAI222','OAI22','OAI33','OR2','OR3','OR4','XNOR2','XOR2']
all_inputs = dict()    #Some global data structures
all_outputs = dict()
all_gates = dict()
all_tags = dict()
all_outtags = dict()
all_pending = dict()
all_status = dict()
all_wires = dict()
all_waittags = dict()
all_appearing_inputs = dict()

os.popen('mkdir -p benchfiles')

for i in range(0, len(module_names)):
    all_inputs[module_names[i]] = []
    all_appearing_inputs[module_names[i]] = []
    all_outputs[module_names[i]] = []
    all_gates[module_names[i]] = dict()
    all_tags[module_names[i]] = []
    all_outtags[module_names[i]] = []
    all_waittags[module_names[i]] = []
    all_pending[module_names[i]] = []
    all_wires[module_names[i]] = []
    all_status[module_names[i]] = False

# if 'vscale_core' in module_names:
#     all_status['vscale_core'] = True  #Skip the top module because it has sub-module instantiations
for i in range(0, len(module_names)):
    if len(all_inputs[module_names[i]]) == 0:
        pattern = re.compile('input.*?;', re.S)  # Find all the input statements
        inputs = pattern.findall(modules[i])
        for input in inputs:
            input = input.replace('input', '').strip(' ;')
            items = input.split(',')
            for item in items:
                item = item.strip()
                if item[0] == '[' and input.find(':') >= 0:
                    begin = int(input[input.find(':') + 1: input.find(']')])
                    end = int(input[input.find('[') + 1: input.find(':')])
                    if begin == 0 and end == 0:
                        all_inputs[module_names[i]].append(module_names[i] + '#' + item[:item.find('[')])
                        continue
                    name = item[item.find(']') + 1:].strip()
                    for j in range(begin, end + 1):
                        all_inputs[module_names[i]].append(module_names[i] + '#' + name + '[' + str(j) + ']')
                else:
                    all_inputs[module_names[i]].append(module_names[i] + '#' + item)
        if modules[i].find('1\'b1') >= 0 and module_names[i] + '#vcc' not in all_inputs[module_names[i]]:
            all_inputs[module_names[i]].append(module_names[i] + '#vcc')
            modules[i] = modules[i].replace('1\'b1', 'vcc')
        if modules[i].find('1\'b0') >= 0 and module_names[i] + '#gnd' not in all_inputs[module_names[i]]:
            all_inputs[module_names[i]].append(module_names[i] + '#gnd')
            modules[i] = modules[i].replace('1\'b0', 'gnd')

    if len(all_outputs[module_names[i]]) == 0:  # Find all the output statements
        pattern = re.compile('output.*?;', re.S)
        outputs = pattern.findall(modules[i])
        for output in outputs:
            output = output.replace('output', '').strip(' ;')
            items = output.split(',')
            for item in items:
                item = item.strip()
                if item[0] == '[' and output.find(':') >= 0:
                    begin = int(output[output.find(':') + 1: output.find(']')])
                    end = int(output[output.find('[') + 1: output.find(':')])
                    name = item[item.find(']') + 1:].strip()
                    for j in range(begin, end + 1):
                        all_outputs[module_names[i]].append(module_names[i] + '#' + name + '[' + str(j) + ']')
                else:
                    all_outputs[module_names[i]].append(module_names[i] + '#' + item)

    if len(all_wires[module_names[i]]) == 0:  # Find all the wire statements
        pattern = re.compile('wire.*?;', re.S)
        wires = pattern.findall(modules[i])
        for wire in wires:
            wire = wire.replace('wire', '').strip(' ;')
            items = wire.split(',')
            for item in items:
                item = item.strip()
                if item[0] == '[' and wire.find(':') >= 0:
                    begin = int(wire[wire.find(':') + 1: wire.find(']')])
                    end = int(wire[wire.find('[') + 1: wire.find(':')])
                    name = item[item.find(']') + 1:].strip()
                    for j in range(begin, end + 1):
                        all_wires[module_names[i]].append(module_names[i] + '#' + name + '[' + str(j) + ']')
                else:
                    all_wires[module_names[i]].append(module_names[i] + '#' + item)

    # for item in all_inputs[module_names[i]]:
    #     ori_item = item[item.find('#') + 1:item.find('[')]
    #     if item.find('[') >= 0 and modules[i].find(ori_item) >= 0:
    #         length = sum([1 for s in all_inputs[module_names[i]] if s.find(item[:item.find('[')]) >= 0])
    #         if modules[i].find(ori_item + ')') >= 0:
    #             modules[i] = modules[i].replace(ori_item + ')', ori_item + '[' + str(length - 1) + ':' + '0])')
    #         elif modules[i].find(ori_item + ',') >= 0:
    #             modules[i] = modules[i].replace(ori_item + ',', ori_item + '[' + str(length - 1) + ':' + '0],')
    #         elif modules[i].find(ori_item + '}') >= 0:
    #             modules[i] = modules[i].replace(ori_item + '}', ori_item + '[' + str(length - 1) + ':' + '0]}')
    #
    # for item in all_outputs[module_names[i]]:
    #     ori_item = item[item.find('#') + 1:item.find('[')]
    #     if item.find('[') >= 0 and modules[i].find(ori_item) >= 0:
    #         length = sum([1 for s in all_outputs[module_names[i]] if s.find(item[:item.find('[')]) >= 0])
    #         if modules[i].find(ori_item + ')') >= 0:
    #             modules[i] = modules[i].replace(ori_item + ')', ori_item + '[' + str(length - 1) + ':' + '0])')
    #         elif modules[i].find(ori_item + ',') >= 0:
    #             modules[i] = modules[i].replace(ori_item + ',', ori_item + '[' + str(length - 1) + ':' + '0],')
    #         elif modules[i].find(ori_item + '}') >= 0:
    #             modules[i] = modules[i].replace(ori_item + '}', ori_item + '[' + str(length - 1) + ':' + '0]}')
    # for item in all_wires[module_names[i]]:
    #     ori_item = item[item.find('#') + 1:item.find('[')]
    #     if item.find('[') >= 0 and modules[i].find(ori_item) >= 0:
    #         length = sum([1 for s in all_wires[module_names[i]] if s.find(item[:item.find('[')]) >= 0])
    #         if modules[i].find(ori_item + ')') >= 0:
    #             modules[i] = modules[i].replace(ori_item + ')', ori_item + '[' + str(length - 1) + ':' + '0])')
    #         elif modules[i].find(ori_item + ',') >= 0:
    #             modules[i] = modules[i].replace(ori_item + ',', ori_item + '[' + str(length - 1) + ':' + '0],')
    #         elif modules[i].find(ori_item + '}') >= 0:
    #             modules[i] = modules[i].replace(ori_item + '}', ori_item + '[' + str(length - 1) + ':' + '0]}')
# file = open('new_whole.v', 'w')
# file.write('\n'.join(modules))
# file.close()
# exit(0)

while True:
    # if 'vscale_core#pipeline_alu_src_b[0]' in all_gates['vscale_core'].keys():#all_inputs['vscale_core']:
    #     print('found!')
    #     exit(0)
    flag0 = True
    if sum([1 for i in range(0, len(module_names)) if all_status[module_names[i]] == False]) == 0:
        break
    if sum([1 for i in range(0, len(module_names)) if all_status[module_names[i]] == False]) == 1:
        flag0 = False
    for i in range(0, len(module_names)):
        if len(all_pending[module_names[i]]) > 0:
            # print(all_pending[module_names[i]])
            print(module_names[i], len(all_pending[module_names[i]]))
            if len(all_pending[module_names[i]]) == 2170:
                exit(0)
        if flag0 and module_names[i] == 'vscale_core':  #First handle other modules, leave the top module to the last
            continue
        if all_status[module_names[i]] == True:
            continue

        module_lines = modules[i].split('\n')
        for line in module_lines:
            line = line.strip()
            if (re.match('[A-Z|a-z].*? .*? .*', line, re.S) or line.find('DFF_')>=0) and line.find('assign') < 0:  # #Recognize all the gate statements
                obj_name = line[: line.find(' ')]
                if obj_name.find('_') >= 0:
                    obj_name = obj_name[: obj_name.find('_')]
                if obj_name in gate_names:
                    input_num = 0
                    tag = line[line.find(' '): line.find('(')].strip()
                    # print(tag)
                    if tag in all_tags[module_names[i]]:
                        continue
                    block = modules[i][modules[i].find(' '+tag+' '):]  #Get the gate blocks
                    block = block[block.find('('): block.find(';')]
                    block = block.replace('\n', '')
                    args = block[1: -1].split(',')
                    # print(args)
                    gate_inputs = []
                    gate_output = ''
                    gate_type = ''
                    if obj_name.find('AND') >= 0:   #Recognize all types of gates
                        if obj_name.find('NAND') < 0:
                            input_num = int(obj_name[obj_name.find('AND') + 3: ])
                            gate_type = 'and'
                        else:
                            input_num = int(obj_name[obj_name.find('NAND') + 4: ])
                            gate_type = 'nand'
                    elif obj_name.find('BUF') >= 0:
                        input_num = 1
                        gate_type = 'buf'
                    elif obj_name.find('INV') >= 0:
                        input_num = 1
                        gate_type = 'not'
                    elif obj_name.find('XOR') >= 0:
                        input_num = int(obj_name[obj_name.find('XOR') + 3: ])
                        gate_type = 'xor'
                    elif obj_name.find('XNOR') >= 0:
                        input_num = int(obj_name[obj_name.find('XNOR') + 4: ])
                        gate_type = 'xnor'
                    elif obj_name.find('OR') >= 0:
                        if obj_name.find('NOR') < 0:
                            input_num = int(obj_name[obj_name.find('OR') + 2: ])
                            gate_type = 'or'
                        else:
                            input_num = int(obj_name[obj_name.find('NOR') + 3: ])
                            gate_type = 'nor'
                    elif obj_name.find('OAI211') >= 0:
                        input_num = 4
                        gate_type = 'OAI211'
                    elif obj_name.find('OAI222') >= 0:
                        input_num = 6
                        gate_type = 'OAI222'
                    elif obj_name.find('OAI221') >= 0:
                        input_num = 5
                        gate_type = 'OAI221'
                    elif obj_name.find('OAI21') >= 0:
                        input_num = 3
                        gate_type = 'OAI21'
                    elif obj_name.find('OAI22') >= 0:
                        input_num = 4
                        gate_type = 'OAI22'
                    elif obj_name.find('OAI33') >= 0: #'AOI211','AOI21','AOI221','AOI222','AOI22'
                        input_num = 6
                        gate_type = 'OAI33'
                    elif obj_name.find('AOI211') >= 0:
                        input_num = 4
                        gate_type = 'AOI211'
                    elif obj_name.find('AOI221') >= 0:
                        input_num = 5
                        gate_type = 'AOI221'
                    elif obj_name.find('AOI222') >= 0:
                        input_num = 6
                        gate_type = 'AOI222'
                    elif obj_name.find('AOI21') >= 0:
                        input_num = 3
                        gate_type = 'AOI21'
                    elif obj_name.find('AOI22') >= 0:
                        input_num = 4
                        gate_type = 'AOI22'
                    elif obj_name.find('HA') >= 0:
                        input_num = 2
                        gate_type = 'HA'
                    elif obj_name.find('FA') >= 0:
                        input_num = 3
                        gate_type = 'FA'
                    elif obj_name.find('MUX2') >= 0:
                        input_num = 3
                        gate_type = 'MUX2'
                    elif obj_name.find('DFF') >= 0:
                        input_num = 2
                        gate_type = 'DFF'
                    else:
                        input_num = len(args)-1
                        gate_type = obj_name

                    flag1 = True         #Check if all the inputs of the gates are the module inputs or the outputs of some gate
                    if gate_type != 'DFF':
                        for j in range(0, input_num):
                            # print(tag, input_num, args)
                            if args[j].find('.') >= 0:
                                if args[j][args[j].find('(') + 1: args[j].find(')')].strip().find(module_names[i]+'#') >= 0:
                                    gate_input = args[j][args[j].find('(') + 1: args[j].find(')')].strip()
                                else:
                                    gate_input = module_names[i] + '#' + args[j][args[j].find('(') + 1: args[j].find(')')].strip()
                                if not (gate_input in all_inputs[module_names[i]] or gate_input in all_gates[
                                    module_names[i]].keys()):
                                    print(gate_input)
                                    flag1 = False
                                    gate_inputs.append(gate_input)
                                    gate_input = gate_input[gate_input.find('#')+1: ]
                                    if gate_input.find('[') >= 0:
                                        gate_input = gate_input[: gate_input.find('[')+1]
                                    # temp = modules[i].replace(' ', '').replace('\n', '')
                                    # if temp.find('.ZN('+gate_input) < 0 and temp.find('.Z('+gate_input) < 0 and temp.find('.CO('+gate_input) < 0 and temp.find('.S('+gate_input) < 0 and temp.find('.QN('+gate_input) < 0 and temp.find('.Q('+gate_input) < 0 :
                                    #     print(gate_input)
                                    # break
                                else:
                                    gate_inputs.append(gate_input)
                                    if gate_input not in all_appearing_inputs[module_names[i]] and gate_input in all_inputs[module_names[i]]:
                                        all_appearing_inputs[module_names[i]].append(gate_input)
                            else:
                                gate_input = module_names[i] + '#' + args[-(j+1)].strip().strip('()')
                                if not (gate_input in all_inputs[module_names[i]] or gate_input in all_gates[
                                    module_names[i]].keys()):
                                    flag1 = False
                                    break
                                else:
                                    gate_inputs.append(gate_input)
                                    if gate_input not in all_appearing_inputs[module_names[i]] and gate_input in all_inputs[module_names[i]]:
                                        all_appearing_inputs[module_names[i]].append(gate_input)
                    if flag1:
                        if True: #tag not in all_waittags:
                            if gate_type != 'HA' and gate_type != 'FA' and gate_type.find('OAI') < 0 and gate_type.find('AOI') < 0 and gate_type.find('MUX') < 0 and gate_type != 'DFF':
                                if args[-1].find('.') >= 0:
                                    gate_output = module_names[i] + '#'+args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    all_gates[module_names[i]][gate_output] = Gate(input_num, gate_inputs, gate_output,gate_type)
                                else:
                                    # print(args)
                                    gate_output = module_names[i] + '#' +args[0].strip()
                                    all_gates[module_names[i]][gate_output] = Gate(input_num, gate_inputs, gate_output,
                                                                                   gate_type)
                            else:
                                if gate_type == 'FA':  #Transform such gates into simple gates
                                    gate_output1 = module_names[i] + '#'+tag+'_FA_xor1'
                                    temp_inputs = [gate_inputs[e] for e in range(0, 2)]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1,'xor')
                                    gate_output2 = module_names[i] + '#'+args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output1, gate_inputs[2]]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2,'xor')
                                    gate_output3 = module_names[i] + '#'+tag+'_FA_or1'
                                    temp_inputs = [gate_inputs[e] for e in range(0, 2)]
                                    all_gates[module_names[i]][gate_output3] = Gate(2, temp_inputs, gate_output3,'or')
                                    gate_output4 = module_names[i] + '#' + tag + '_FA_and1'
                                    temp_inputs = [gate_output3, gate_inputs[2]]
                                    all_gates[module_names[i]][gate_output4] = Gate(2, temp_inputs, gate_output4, 'and')
                                    gate_output5 = module_names[i] + '#' + tag + '_FA_and2'
                                    temp_inputs = [gate_inputs[e] for e in range(0, 2)]
                                    all_gates[module_names[i]][gate_output5] = Gate(2, temp_inputs, gate_output5, 'and')
                                    gate_output6 = module_names[i] + '#'+args[-2][args[-2].find('(') + 1: args[-2].find(')')].strip()
                                    temp_inputs = [gate_output4, gate_output5]
                                    all_gates[module_names[i]][gate_output6] = Gate(2, temp_inputs, gate_output6, 'or')
                                elif gate_type == 'HA':
                                    gate_output1 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    all_gates[module_names[i]][gate_output1] = Gate(2, gate_inputs, gate_output1, 'xor')
                                    gate_output2 = module_names[i] + '#' + args[-2][args[-2].find('(') + 1: args[-2].find(')')].strip()
                                    all_gates[module_names[i]][gate_output2] = Gate(2, gate_inputs, gate_output2, 'and')
                                elif gate_type == 'MUX2':
                                    gate_output1 = module_names[i] + '#' + tag + '_MUX_not1'
                                    temp_inputs = [gate_inputs[2]]
                                    all_gates[module_names[i]][gate_output1] = Gate(1, temp_inputs, gate_output1, 'not')
                                    gate_output2 = module_names[i] + '#' + tag + '_MUX_and1'
                                    temp_inputs = [gate_output1, gate_inputs[0]]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output1, 'and')
                                    gate_output3 = module_names[i] + '#' + tag + '_MUX_and2'
                                    temp_inputs = [gate_inputs[1], gate_inputs[2]]
                                    all_gates[module_names[i]][gate_output3] = Gate(2, temp_inputs, gate_output3, 'and')
                                    gate_output4 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output2, gate_output3]
                                    all_gates[module_names[i]][gate_output4] = Gate(2, temp_inputs, gate_output4, 'or')
                                elif gate_type == 'OAI211':
                                    gate_output1 = module_names[i] + '#' + tag + '_OAI_or1'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'or')
                                    gate_output2 = module_names[i] + '#' + tag + '_OAI_and1'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3], gate_output1]
                                    all_gates[module_names[i]][gate_output2] = Gate(3, temp_inputs, gate_output2, 'and')
                                    gate_output3 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output2]
                                    all_gates[module_names[i]][gate_output3] = Gate(1, temp_inputs, gate_output2, 'not')
                                elif gate_type == 'OAI21':
                                    gate_output1 = module_names[i] + '#' + tag + '_OAI_or1'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'or')
                                    gate_output2 = module_names[i] + '#' + tag + '_OAI_and1'
                                    temp_inputs = [gate_inputs[2], gate_output1]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'and')
                                    gate_output3 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output2]
                                    all_gates[module_names[i]][gate_output3] = Gate(1, temp_inputs, gate_output2, 'not')
                                elif gate_type == 'OAI221':
                                    gate_output1 = module_names[i] + '#' + tag + '_OAI_or1'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'or')
                                    gate_output2 = module_names[i] + '#' + tag + '_OAI_or2'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3]]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'or')
                                    gate_output3 = module_names[i] + '#' + tag + '_OAI_and1'
                                    temp_inputs = [gate_inputs[4], gate_output2, gate_output1]
                                    all_gates[module_names[i]][gate_output3] = Gate(3, temp_inputs, gate_output3, 'and')
                                    gate_output4 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output3]
                                    all_gates[module_names[i]][gate_output4] = Gate(1, temp_inputs, gate_output4, 'not')
                                elif gate_type == 'OAI222':
                                    gate_output0 = module_names[i] + '#' + tag + '_OAI_or0'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output0] = Gate(2, temp_inputs, gate_output0, 'or')
                                    gate_output1 = module_names[i] + '#' + tag + '_OAI_or1'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'or')
                                    gate_output2 = module_names[i] + '#' + tag + '_OAI_or2'
                                    temp_inputs = [gate_inputs[5], gate_inputs[4]]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'or')
                                    gate_output3 = module_names[i] + '#' + tag + '_OAI_and1'
                                    temp_inputs = [gate_output0, gate_output2, gate_output1]
                                    all_gates[module_names[i]][gate_output3] = Gate(3, temp_inputs, gate_output3, 'and')
                                    gate_output4 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output3]
                                    all_gates[module_names[i]][gate_output4] = Gate(1, temp_inputs, gate_output4, 'not')
                                elif gate_type == 'OAI22':
                                    # print(tag)
                                    gate_output0 = module_names[i] + '#' + tag + '_OAI_or0'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output0] = Gate(2, temp_inputs, gate_output0, 'or')
                                    gate_output1 = module_names[i] + '#' + tag + '_OAI_or1'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'or')
                                    gate_output2 = module_names[i] + '#' + tag + '_OAI_and1'
                                    temp_inputs = [gate_output0, gate_output1]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'and')
                                    gate_output3 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(
                                        ')')].strip()
                                    temp_inputs = [gate_output2]
                                    all_gates[module_names[i]][gate_output3] = Gate(1, temp_inputs, gate_output3, 'not')
                                elif gate_type == 'OAI33':
                                    gate_output0 = module_names[i] + '#' + tag + '_OAI_or0'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1], gate_inputs[2]]
                                    all_gates[module_names[i]][gate_output0] = Gate(3, temp_inputs, gate_output0, 'or')
                                    gate_output1 = module_names[i] + '#' + tag + '_OAI_or1'
                                    temp_inputs = [gate_inputs[3], gate_inputs[4], gate_inputs[5]]
                                    all_gates[module_names[i]][gate_output1] = Gate(3, temp_inputs, gate_output1, 'or')
                                    gate_output2 = module_names[i] + '#' + tag + '_OAI_and1'
                                    temp_inputs = [gate_output0, gate_output1]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'and')
                                    gate_output3 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(
                                        ')')].strip()
                                    temp_inputs = [gate_output2]
                                    all_gates[module_names[i]][gate_output3] = Gate(1, temp_inputs, gate_output3, 'not')
                                elif gate_type == 'AOI211':
                                    gate_output1 = module_names[i] + '#' + tag + '_AOI_and1'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'and')
                                    gate_output2 = module_names[i] + '#' + tag + '_AOI_or1'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3], gate_output1]
                                    all_gates[module_names[i]][gate_output2] = Gate(3, temp_inputs, gate_output2, 'or')
                                    gate_output3 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(
                                        ')')].strip()
                                    temp_inputs = [gate_output2]
                                    all_gates[module_names[i]][gate_output3] = Gate(1, temp_inputs, gate_output2, 'not')
                                elif gate_type == 'AOI221':
                                    gate_output1 = module_names[i] + '#' + tag + '_AOI_and1'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'and')
                                    gate_output2 = module_names[i] + '#' + tag + '_AOI_and2'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3]]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'and')
                                    gate_output3 = module_names[i] + '#' + tag + '_AOI_or1'
                                    temp_inputs = [gate_inputs[4], gate_output2, gate_output1]
                                    all_gates[module_names[i]][gate_output3] = Gate(3, temp_inputs, gate_output3, 'or')
                                    gate_output4 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output3]
                                    all_gates[module_names[i]][gate_output4] = Gate(1, temp_inputs, gate_output4, 'not')
                                elif gate_type == 'AOI21':
                                    gate_output1 = module_names[i] + '#' + tag + '_AOI_and1'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'and')
                                    gate_output2 = module_names[i] + '#' + tag + '_AOI_or1'
                                    temp_inputs = [gate_inputs[2], gate_output1]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'or')
                                    gate_output3 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output2]
                                    all_gates[module_names[i]][gate_output3] = Gate(1, temp_inputs, gate_output2, 'not')
                                elif gate_type == 'AOI222':
                                    gate_output0 = module_names[i] + '#' + tag + '_AOI_and0'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output0] = Gate(2, temp_inputs, gate_output0, 'and')
                                    gate_output1 = module_names[i] + '#' + tag + '_AOI_and1'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'and')
                                    gate_output2 = module_names[i] + '#' + tag + '_AOI_and2'
                                    temp_inputs = [gate_inputs[4], gate_inputs[5]]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'and')
                                    gate_output3 = module_names[i] + '#' + tag + '_AOI_or1'
                                    temp_inputs = [gate_output0, gate_output2, gate_output1]
                                    all_gates[module_names[i]][gate_output3] = Gate(3, temp_inputs, gate_output3, 'or')
                                    gate_output4 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(')')].strip()
                                    temp_inputs = [gate_output3]
                                    all_gates[module_names[i]][gate_output4] = Gate(1, temp_inputs, gate_output4, 'not')
                                elif gate_type == 'AOI22':
                                    gate_output0 = module_names[i] + '#' + tag + '_AOI_and0'
                                    temp_inputs = [gate_inputs[0], gate_inputs[1]]
                                    all_gates[module_names[i]][gate_output0] = Gate(2, temp_inputs, gate_output0, 'and')
                                    gate_output1 = module_names[i] + '#' + tag + '_AOI_and1'
                                    temp_inputs = [gate_inputs[2], gate_inputs[3]]
                                    all_gates[module_names[i]][gate_output1] = Gate(2, temp_inputs, gate_output1, 'and')
                                    gate_output2 = module_names[i] + '#' + tag + '_AOI_or1'
                                    temp_inputs = [gate_output0, gate_output1]
                                    all_gates[module_names[i]][gate_output2] = Gate(2, temp_inputs, gate_output2, 'or')
                                    gate_output3 = module_names[i] + '#' + args[-1][args[-1].find('(') + 1: args[-1].find(
                                        ')')].strip()
                                    temp_inputs = [gate_output2]
                                    all_gates[module_names[i]][gate_output3] = Gate(1, temp_inputs, gate_output3, 'not')
                                elif gate_type == 'DFF':
                                    for j in range(0, input_num):
                                        arg_name = module_names[i] + '#' + args[j][args[j].find('(') + 1: args[j].find(
                                        ')')].strip()
                                        if arg_name not in all_inputs[module_names[i]] and arg_name not in all_outputs[module_names[i]]:
                                            all_outputs[module_names[i]].append(arg_name)
                                    for j in range(input_num, len(args)):
                                        arg_name = module_names[i] + '#' + args[j][args[j].find('(') + 1: args[j].find(
                                            ')')].strip()
                                        if arg_name not in all_inputs[module_names[i]] and arg_name not in all_outputs[module_names[i]]:
                                            all_inputs[module_names[i]].append(arg_name)
                                            # print(arg_name)
                                        elif arg_name in all_outputs[module_names[i]]:
                                            all_outputs[module_names[i]].remove(arg_name)
                                            all_inputs[module_names[i]].append(arg_name)
                        # if tag not in all_waittags:
                        #     all_waittags[module_names[i]].append(tag)
                        if flag1:
                            all_tags[module_names[i]].append(tag)
                            if tag in all_pending[module_names[i]]:
                                all_pending[module_names[i]].remove(tag)
                            # if tag in all_waittags[module_names[i]]:
                            #     all_waittags[module_names[i]].remove(tag)
                        else:
                            if tag not in all_pending[module_names[i]]:
                                all_pending[module_names[i]].append(tag)
                    else:
                        if tag not in all_pending[module_names[i]]:
                            all_pending[module_names[i]].append(tag)

            elif re.match('.*?assign .*?=.*?;', line, re.S):
                lhs = line[line.find('assign')+7: line.find('=')].strip()
                rhs = line[line.find('=')+1: line.find(';')].strip()
                # print(rhs)
                if module_names[i] + '#' +rhs in all_inputs[module_names[i]] or module_names[i]+'#' +rhs in all_gates[module_names[i]].keys():
                    gate_output = module_names[i] + '#' + lhs
                    if gate_output not in list(all_gates[module_names[i]].keys()):
                        all_gates[module_names[i]][gate_output] = Gate(1, [module_names[i] + '#' +rhs], gate_output, 'buf')
                    if rhs in all_pending[module_names[i]]:
                        all_pending[module_names[i]].remove(rhs)
                    if module_names[i] + '#'+rhs not in all_appearing_inputs[module_names[i]] and module_names[i] + '#'+rhs in all_inputs[
                        module_names[i]]:
                        all_appearing_inputs[module_names[i]].append(module_names[i] + '#'+rhs)
                else:
                    if rhs not in all_pending[module_names[i]]:
                        all_pending[module_names[i]].append(rhs)

                    # print(gate_output)

            #TODO: These are for module instantiation statements, which have not been successfully tuned
            # elif line[:line.find(' ')].strip() in module_names and line[:line.find(' ')].strip() != module_names[i]:
            #     name = line[:line.find(' ')].strip()
            #     tag = line[line.find(' '): line.find('(')].strip()
            #     if tag in all_tags[module_names[i]]:
            #         continue
            #     block = modules[i][modules[i].find(' '+tag+' '):]
            #     block = block[block.find('('): block.find(';')]
            #     block = block.replace('\n', '')
            #     # for item in all_inputs[module_names[i]]:
            #     #     ori_item = item[item.find('#') + 1:item.find('[')]
            #     #     if item.find('[') >= 0 and block.find(ori_item) >= 0:
            #     #         length = sum([1 for s in all_inputs[module_names[i]] if s.find(item[:item.find('[')]) >= 0])
            #     #         if block.find(ori_item+')') >= 0:
            #     #             block = block.replace(ori_item+')', ori_item+'['+str(length-1)+':'+'0])')
            #     #         elif block.find(ori_item+',') >= 0:
            #     #             block = block.replace(ori_item+',', ori_item+'['+str(length-1)+':'+'0],')
            #     #         elif block.find(ori_item+'}') >= 0:
            #     #             block = block.replace(ori_item+'}', ori_item+'['+str(length-1)+':'+'0]}')
            #     # for item in all_outputs[module_names[i]]:
            #     #     ori_item = item[item.find('#') + 1:item.find('[')]
            #     #     if item.find('[') >= 0 and block.find(ori_item) >= 0:
            #     #         length = sum([1 for s in all_outputs[module_names[i]] if s.find(item[:item.find('[')]) >= 0])
            #     #         if block.find(ori_item + ')') >= 0:
            #     #             block = block.replace(ori_item + ')', ori_item + '[' + str(length - 1) + ':' + '0])')
            #     #         elif block.find(ori_item + ',') >= 0:
            #     #             block = block.replace(ori_item + ',', ori_item + '[' + str(length - 1) + ':' + '0],')
            #     #         elif block.find(ori_item + '}') >= 0:
            #     #             block = block.replace(ori_item + '}', ori_item + '[' + str(length - 1) + ':' + '0]}')
            #     # for item in all_wires[module_names[i]]:
            #     #     ori_item = item[item.find('#') + 1:item.find('[')]
            #     #     if item.find('[') >= 0 and block.find(ori_item) >= 0:
            #     #         length = sum([1 for s in all_wires[module_names[i]] if s.find(item[:item.find('[')]) >= 0])
            #     #         if block.find(ori_item + ')') >= 0:
            #     #             block = block.replace(ori_item + ')', ori_item + '[' + str(length - 1) + ':' + '0])')
            #     #         elif block.find(ori_item + ',') >= 0:
            #     #             block = block.replace(ori_item + ',', ori_item + '[' + str(length - 1) + ':' + '0],')
            #     #         elif block.find(ori_item + '}') >= 0:
            #     #             block = block.replace(ori_item + '}', ori_item + '[' + str(length - 1) + ':' + '0]}')
            #     args = block[1: -1].split('.')
            #     args = args[1:]
            #     flag2 = True
            #     input_num = 0
            #     inputs = []
            #
            #     for j in range(0, len(all_inputs[name])):
            #         input = all_inputs[name][j]
            #         if input.find('[') >= 0:
            #             if input[: input.find('[')] not in inputs:
            #                 inputs.append(input[: input.find('[')])
            #         else:
            #             inputs.append(input)
            #
            #     outputs = []
            #     for j in range(0, len(all_outputs[name])):
            #         output = all_outputs[name][j]
            #         if output.find('[') >= 0:
            #             if output[: output.find('[')] not in outputs:
            #                 outputs.append(output[: output.find('[')])
            #         else:
            #             outputs.append(output)
            #
            #     for j in range(0, len(inputs)):
            #         arg = args[j]
            #         arg = arg[arg.find('('): arg.find(')')].strip('() \n').strip()
            #         if arg.find('{') < 0:  # (gate_input in all_inputs[module_names[i]] or gate_input in all_gates[module_names[i]].keys()):
            #             if arg != '1\'b0' and arg != '1\'b1' and not (module_names[i]+'#'+arg in all_inputs[module_names[i]] or module_names[i]+'#'+arg in all_gates[module_names[i]].keys() or module_names[i]+'#'+arg in all_outputs[module_names[i]]):
            #                 flag2 = False
            #                 break
            #         else:
            #             wires = arg.strip('{}').strip().split(',')
            #             for wire in wires:
            #                 wire = wire.strip()
            #                 if wire != '1\'b0' and wire != '1\'b1':
            #                     if wire.find(':') < 0 and not (module_names[i]+'#'+wire in all_inputs[module_names[i]] or module_names[i]+'#'+wire in all_gates[module_names[i]].keys() or module_names[i]+'#'+wire in all_outputs[module_names[i]]):
            #                         flag2 = False
            #                         break
            #                     elif wire.find(':') >= 0:
            #                         start = int(wire[wire.find(':')+1: wire.find(']')])
            #                         end = int(wire[wire.find('[')+1: wire.find(':')])
            #                         for k in range(start, end+1):
            #                             array_name = wire[: wire.find('[')+1] + str(k) +']'
            #                             # print(array_name)
            #                             if not (module_names[i]+'#'+array_name in all_inputs[module_names[i]] or module_names[i]+'#'+array_name in all_gates[module_names[i]].keys() or module_names[i]+'#'+array_name in all_outputs[module_names[i]]):
            #                                 flag2 = False
            #                                 break
            #                         if not flag2:
            #                             break
            #             if not flag2:
            #                 break
            #     if flag2:
            #         # print(tag)
            #         for j in range(0, len(inputs)):
            #             arg = args[j].strip()
            #             # print(arg)
            #             arg_name = arg[: arg.find('(')].strip()
            #             input_index = inputs.index(name+'#'+arg_name)
            #             # print(input_index, inputs, name+'#'+arg_name)
            #             arg = arg[arg.find('('): arg.find(')')].strip('() \n').strip()
            #             # print(arg)
            #             if arg.find('{') < 0:
            #                 if arg == '1\'b0':
            #                     all_gates[module_names[i]][inputs[input_index]] = Gate(1, ['gnd'], inputs[input_index], 'buf')
            #                 elif arg == '1\'b1':
            #                     all_gates[module_names[i]][inputs[input_index]] = Gate(1, ['gcc'], inputs[input_index], 'buf')
            #                 elif arg.find(':') >= 0:
            #                     start = int(arg[arg.find(':') + 1: arg.find(']')])
            #                     end = int(arg[arg.find('[') + 1: arg.find(':')])
            #                     for k in range(start, end + 1):
            #                         all_gates[module_names[i]][inputs[input_index] + '[' + str(k) + ']'] = Gate(1, [
            #                             module_names[i] + '#' + arg[:arg.find('[')]+'['+str(k)+']'], inputs[input_index] + '[' + str(k-start) + ']','buf')
            #                 else:
            #                     all_gates[module_names[i]][inputs[input_index]] = Gate(1, [
            #                         module_names[i] + '#' + arg], inputs[input_index], 'buf')
            #             else:
            #                 wires = arg.strip('{}').strip().split(',')
            #                 # print(wires)
            #                 count = 0
            #                 for k in range(len(wires)-1, -1, -1):
            #                     wire = wires[k].strip()
            #                     if wire.find(':') < 0:
            #                         all_gates[module_names[i]][inputs[input_index] + '[' + str(count) + ']'] = Gate(
            #                             1, [module_names[i] + '#' + wire],
            #                             inputs[input_index] + '[' + str(count) + ']', 'buf')
            #                         count += 1
            #                     else:
            #                         start = int(wire[wire.find(':') + 1: wire.find(']')])
            #                         end = int(wire[wire.find('[') + 1: wire.find(':')])
            #                         for l in range(start, end+1):
            #                             all_gates[module_names[i]][inputs[input_index] + '[' + str(count) + ']'] = Gate(1, [module_names[i] + '#' + wire[:wire.find('[')]+'['+str(l)+']'], inputs[input_index] + '[' + str(count) + ']', 'buf')
            #                             count += 1
            #         for key in all_gates[name].keys():
            #             all_gates[module_names[i]][key] = all_gates[name][key]
            #         if tag in all_pending[module_names[i]]:
            #             all_pending[module_names[i]].remove(tag)
            #         all_tags[module_names[i]].append(tag)
            #     else:
            #         if tag not in all_pending[module_names[i]]:
            #             all_pending[module_names[i]].append(tag)
            #
            #     if tag not in all_outtags[module_names[i]]:
            #         for j in range(len(inputs), len(args)):
            #             arg = args[j].strip()
            #             # print(arg)
            #             arg_name = arg[: arg.find('(')].strip()
            #             output_index = outputs.index(name + '#' + arg_name)
            #             arg = arg[arg.find('('): arg.find(')')].strip('() \n').strip()
            #             if arg.find('{') < 0:
            #                 if arg.find(':') >= 0:
            #                     start = int(arg[arg.find(':') + 1: arg.find(']')])
            #                     end = int(arg[arg.find('[') + 1: arg.find(':')])
            #                     for k in range(start, end + 1):
            #                         all_gates[module_names[i]][
            #                             module_names[i] + '#' + arg[:arg.find('[')] + '[' + str(k) + ']'] = Gate(1, [
            #                             outputs[output_index] + '[' + str(k - start) + ']'], module_names[i] + '#' + arg[
            #                                                                                                          :arg.find(
            #                                                                                                              '[')] + '[' + str(
            #                                                                                                              k) + ']',
            #                                                                                                      'buf')
            #                 else:
            #                     all_gates[module_names[i]][module_names[i] + '#' + arg] = Gate(1, [outputs[output_index]],
            #                                                                                    module_names[i] + '#' + arg,
            #                                                                                    'buf')
            #             else:
            #                 wires = arg.strip('{}').strip().split(',')
            #                 count = 0
            #                 for k in range(len(wires) - 1, -1, -1):
            #                     # print(k)
            #                     wire = wires[k].strip()
            #                     if wire.find(':') < 0:
            #                         # print(module_names[i]+'#'+wire)
            #                         all_gates[module_names[i]][module_names[i] + '#' + wire] = Gate(1,
            #                                                                                         [outputs[output_index]],
            #                                                                                         module_names[
            #                                                                                             i] + '#' + wire,
            #                                                                                         'buf')
            #                         count += 1
            #                     else:
            #                         start = int(wire[wire.find(':') + 1: wire.find(']')])
            #                         end = int(wire[wire.find('[') + 1: wire.find(':')])
            #                         for l in range(start, end + 1):
            #                             # print(tag, module_names[i] + '#' + wire[:wire.find('[')]+'['+str(l)+']')
            #                             all_gates[module_names[i]][
            #                                 module_names[i] + '#' + wire[:wire.find('[')] + '[' + str(l) + ']'] = Gate(
            #                                 1, [outputs[output_index] + '[' + str(count) + ']'],
            #                                 module_names[i] + '#' + wire[:wire.find('[')] + '[' + str(l) + ']', 'buf')
            #                             count += 1
            #         all_outtags[module_names[i]].append(tag)

        if len(all_pending[module_names[i]]) == 0: #This means the process of a module has been completed
            all_status[module_names[i]] = True
            print(module_names[i])


for i in range(0, len(module_names)):  #Generate bench files
    # if module_names[i] == 'vscale_core':
    #     continue
    seq_num = 1
    bench_text = ''
    gate_dict = dict()
    for j in range(0, len(all_appearing_inputs[module_names[i]])):
        gate_dict[all_appearing_inputs[module_names[i]][j]] = seq_num
        bench_text = bench_text + 'INPUT(G' + str(seq_num) + 'gat)\n'  #Add inputs of the bench
        seq_num = seq_num + 1

    for j in range(0, len(all_outputs[module_names[i]])):
        if all_outputs[module_names[i]][j] in all_gates[module_names[i]].keys():
            gate_dict[all_outputs[module_names[i]][j]] = seq_num
            bench_text = bench_text + 'OUTPUT(G' + str(seq_num) + 'gat)\n'  #Add outputs of the bench
            seq_num = seq_num + 1

    bench_text = bench_text + '\n'

    gate_names = list(all_gates[module_names[i]].keys())
    for j in range(0, len(gate_names)):
        if gate_names[j] not in all_inputs[module_names[i]] and gate_names[j] not in all_outputs[module_names[i]]:
            gate_dict[gate_names[j]] = seq_num
            seq_num = seq_num + 1

    for j in range(0, len(gate_names)):
        gat_ins = []
        for gat_in in all_gates[module_names[i]][gate_names[j]].inputs:
            gat_ins.append('G'+str(gate_dict[gat_in])+'gat')
        bench_text = bench_text+'G'+str(gate_dict[gate_names[j]])+'gat = '+all_gates[module_names[i]][gate_names[j]].type+'('+', '.join(gat_ins)+')\n'
    file = open('./benchfiles/'+module_names[i]+'.bench', 'w')
    file.write(bench_text)
    file.close()





