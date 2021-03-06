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

import phase_disassembler_native
import phase_disassembler_jvm

def init_argparser(argparser):
    subparsers = argparser.add_subparsers(help='Input format')
    native_parser = subparsers.add_parser('native')
    jvm_parser = subparsers.add_parser('jvm')
    phase_disassembler_native.init_argparser(native_parser)
    phase_disassembler_jvm.init_argparser(jvm_parser)

def init():
    pass

def apply_options(options):
    pass

def get_name():
    return "phase_disassembler"

def do_phase(context):
    if context.options.input_type == 'native':
        return phase_disassembler_native.do_phase(context)
    elif context.options.input_type == 'jvm':
        return phase_disassembler_jvm.do_phase(context)
    raise Exception("Unknown input type")
