#   Copyright 2016 Sergey Melnikov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re
import subprocess

import cfg_types


def try_routine_begin(line):
    return re.match('^([0-9_a-zA-Z@]+)\:$', line)

def parse_line(line):
    return re.match('[ ]+(?P<addr>[0-9a-fA-F]+)\:\s+(?P<encoding>(:?[0-9a-fA-F]{2}[ ])+)\s+(?P<mnemonic>[^ \t]+)(:?\t(?P<args>.*))?$', line)

def fix_jmp_address(inst):
    offset = int(inst.args, 10)
    target_addr = inst.addr + inst.size + offset
    inst.args = '0x%x' % target_addr
    inst.target_addr = target_addr

def create_instruction_from_line(line):
    gd = parse_line(line).groupdict()
    inst = cfg_types.instruction()
    inst.mnemonic = gd['mnemonic']
    inst.args = gd['args'] if 'args' in gd and gd['args'] != None else ''
    inst.addr = int(gd['addr'], 16)
    inst.size = len(gd['encoding'])/3
    inst.encoding = gd['encoding']
    if inst.mnemonic[0] == 'j':
        fix_jmp_address(inst)
    return inst
        
def get_disassemble_llvm_objdump(exe_path, routine_name):
    proc = subprocess.Popen(['llvm-objdump-3.4', '-d', exe_path], stdout=subprocess.PIPE)
    l_ = proc.stdout.readline()
    routine_to_dump = False
    instructions = []
    while l_ != '':
        l = l_.strip("\r\n")
        
        if routine_to_dump and l == '':
            break

        if routine_to_dump:
            inst = create_instruction_from_line(l)
            instructions.append(inst)

        g = try_routine_begin(l)
        if g:
            if g.group(1) == routine_name:
                routine_to_dump = True
        
        l_ = proc.stdout.readline()
    return instructions

def get_disassemble_llvm_objdump_by_addrs(exe_path, start_addr, end_addr):
    proc = subprocess.Popen(['llvm-objdump-3.4', '-d', exe_path], stdout=subprocess.PIPE)
    l_ = proc.stdout.readline()
    start_regexp = "^[ ]+[0-9a-fA-F]*%s\:.*$" % start_addr
    end_regexp = "^[ ]+[0-9a-fA-F]*%s\:.*$" % end_addr
    in_region_to_dump = False
    instructions = []
    while l_ != '':
        l = l_.strip("\r\n")
        
        if re.match(start_regexp, l):
            in_region_to_dump = True
        if in_region_to_dump:
            #print l
            inst = create_instruction_from_line(l)
            instructions.append(inst)            
        if re.match(end_regexp, l):
            while l_ != '':
                l_ = proc.stdout.readline()
            break
        l_ = proc.stdout.readline()
    return instructions

def is_jump_instruction(inst):
    return inst.mnemonic[0] == 'j'

def is_conditional_jump(inst):
    return inst.mnemonic[0] == 'j' and inst.mnemonic != 'jmp'

def is_unconditional_jump(inst):
    return inst.mnemonic == 'jmp'

def is_last_bb_instruction(inst):
    return is_jump_instruction(inst) or inst.mnemonic == 'call' or inst.mnemonic == 'ret'

def extract_cfg(context, listing):
    lines = []
    current_bb = cfg_types.basic_block()
    for inst in listing:
        current_bb.inst.append(inst)
        if is_last_bb_instruction(inst):
            cfg_types.append_bb(context, current_bb)
            current_bb = cfg_types.basic_block()
    if len(current_bb.inst) > 0:
        cfg_types.append_bb(context, current_bb)

    bb_to_parse = cfg_types.all_bbs(context)
    while len(bb_to_parse):
        bb = bb_to_parse[0]
        bb_to_parse.remove(bb)
        if is_jump_instruction(bb.inst[-1]):
            target_addr = bb.inst[-1].target_addr
            old_bb, new_bb = cfg_types.split_bb_at(context, target_addr)
            if old_bb != new_bb:
                bb_to_parse.append(new_bb)
            cfg_types.create_edge_by_bb(context, bb, new_bb, cfg_types.edge.CONDITION_JUMP)

    all_bbs = cfg_types.all_bbs(context)
    for bb in all_bbs:
        if not is_unconditional_jump(bb.inst[-1]):
            end_addr = bb.end()
            next_bb = cfg_types.get_bb_by_addr(context, end_addr + 1)
            if next_bb != None:
                type_ = cfg_types.edge.UNKNOWN
                if is_conditional_jump(bb.inst[-1]):
                    type_ = cfg_types.edge.CONDITION_THROUGH
                else:
                    type_ = cfg_types.edge.CONTINUE
                cfg_types.create_edge_by_bb(context, bb, next_bb, type_)

def init_argparser(argparser):
    argparser.add_argument('--executable', dest='executable', required=True)
    argparser.add_argument('--routine', dest='routine', required=False)
    argparser.add_argument('--start-address', dest='start_address')
    argparser.add_argument('--end-address', dest='end_address')

def init():
    pass

def apply_options(options):
    pass

def get_name():
    return "phase_disassembler"

def do_phase(context):
    listing = None
    if context.options.routine and context.options.routine != '':
        listing = get_disassemble_llvm_objdump(context.options.executable, context.options.routine)
    elif context.options.start_address and context.options.end_address:
        listing = get_disassemble_llvm_objdump_by_addrs(context.options.executable, context.options.start_address, context.options.end_address)
    extract_cfg(context, listing)
    return True
