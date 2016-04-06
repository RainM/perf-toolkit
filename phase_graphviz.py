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
import os
import sys
import subprocess

import cfg_types


def output_header(out):
    s = "digraph g {\n\
        graph [fontsize=30 labelloc=\"t\" label=\"\" splines=true overlap=false fontname = \"Courier\"];\n\
        node [fontname = \"Courier\"];\n\
        edge [fontname = \"Courier\"];\n"
    #print s
    out.write(s)
    out.write("\n")

def output_tail(out):
    s = "}\n"
    #print s
    out.write(s)
    out.write("\n")

def output_bb(out, bb):
    listing = '\l'.join([x.to_string() for x in bb.inst]) + '\l'
    s = '"0x%x" [label="%s" shape = "record"]' % ( bb.begin(), listing)
    #print s
    out.write(s)
    out.write("\n")
    return

def output_edge(out, edge):
    s = '"0x%x" -> "0x%x"' % (edge.from_, edge.to)
    #print s
    out.write(s)
    out.write("\n")

def output_loop(out, loop, idx):
    s = "subgraph cluster_%d {" % idx
    #print s
    out.write(s)
    out.write("\n")
    for bb in loop.bbs:
        output_bb(out, bb)
    s = "}"
    #print s
    out.write(s)
    out.write("\n")

def output_content(out, context):
    loop_bbs = []
    idx = 0
    for loop in context.loops:
        for bb in loop.bbs:
            loop_bbs += [bb]
        output_loop(out, loop, idx)
        idx += 1

    for bb in cfg_types.all_bbs(context):
        if not bb in loop_bbs:
            output_bb(out, bb)
    for edge in cfg_types.all_edges(context):
        output_edge(out, edge)
    return

def init_argparser(argparser):
    argparser.add_argument('--output-format', default='png')
    argparser.add_argument('--output', default='output.png')
    argparser.add_argument('--dump-to-file', default=None)

def init():
    pass

def apply_options(options):
    pass

def get_name():
    return "Export to GRAPHVIZ"

def do_phase(context):
    proc = subprocess.Popen(['dot', '-T' + context.options.output_format, '-o', context.options.output], stdin=subprocess.PIPE)
    out = proc.stdin
    output_header(out)
    output_content(out, context)
    output_tail(out)
    out.close()
    proc.wait()
    out_file_name = context.options.dump_to_file
    if out_file_name:
        out_stm = None
        if out_file_name == 'stdout':
            out_stm = sys.stdout
        else:
            out_stm = open(out_file_name, "w")

        output_header(out_stm)
        output_content(out_stm, context)
        output_tail(out_stm)

        if out_file_name != 'stdout':
            out_stm.close()
    return True
