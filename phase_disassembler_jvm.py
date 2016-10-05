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

def init_argparser(argparser):
    argparser.add_argument('--compilation_output', dest='compilation_out', required=False)
    argparser.add_argument('--routine', dest='routine')

def init():
    pass

def apply_options(options):
    pass

def get_name():
    return "phase_disassembler_jvm"

def do_phase(context):
    return True
