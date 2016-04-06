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

class instruction:
    def __init__(self):
        self.mnemonic = ''
        self.args = ''
        self.addr = 0
        self.size = 0
        self.encoding = ''
        self.target_addr = 0

    def __str__(self):
        #return "0x%x\t%s[%d]\t%s\t%s" % (self.addr, self.encoding, self.size, self.mnemonic, self.args)
        #return "0x%x\t%s\t%s\t%s" % (self.addr, self.encoding, self.mnemonic, self.args)
        return "0x%x\t%s\t%s" % (self.addr, self.mnemonic, self.args)
    
    def to_string(self):
        return "0x%x\t%s\t%s" % (self.addr, self.mnemonic, self.args)

class basic_block:
    def __init__(self):
        self.inst = []
    
    def begin(self):
        return self.inst[0].addr

    def end(self):
        return self.inst[-1].addr + self.inst[-1].size - 1

    def __str__(self):
        return 'BB: {0x%x:0x%x}' % (self.begin(), self.end())

class edge:
    UNKNOWN = 0
    CONTINUE = 1
    CONDITION_THROUGH = 2
    CONDITION_JUMP = 3
    UNCONDITION = 4

    def __init__(self):
        self.from_ = 0
        self.to = 0
        self.type_ = self.UNKNOWN
        self.from_bb = None
        self.to_bb = None

    def __str__(self):
        return 'Edge 0x%x -> 0x%x' % (self.from_, self.to)

class loop:
    def __init__(self):
        self.bbs = []
        self.total = 0
        self.lines = []
        self.addrs = []

    def __str__(self):
        result = "Loop:\n\t" + "\n\t".join(['%s' % x for x in self.bbs])
        return result

class context:
    def __init__(self):
        self.bbs = []
        self.edges = []
        self.function_name = ''
        self.options = None
        self.loops = []

def get_bb_by_addr(context, addr):
    for bb in context.bbs:
        if addr == bb.begin():
            return bb
    return None

def all_edges(context):
    return context.edges[:]

def all_bbs(context):
    return context.bbs[:]

def append_bb(context, bb):
    context.bbs.append(bb)

def append_edge(context, edge):
    context.edges.append(edge)

def get_edges_by_from(context, from_addr):
    result = []
    for edge in context.edges:
        if edge.from_ == from_addr:
            result.append(edge)
    return result

def create_edge_by_bb(context, from_bb, to_bb, type_):
    e = edge()
    e.from_ = from_bb.begin()
    e.to = to_bb.begin()
    e.type_ = type_
    e.from_bb = from_bb
    e.to_bb = to_bb
    #print 'Edge: %s -> %s' % (from_bb, to_bb)
    context.edges.append(e)

def split_bb_at(context, addr):
    for bb in context.bbs:
        if bb.begin() == addr:
            return bb, bb
        elif bb.begin() < addr and bb.end() > addr:
            #print 'BB to split: %s' % bb
            for idx in range(1, len(bb.inst) - 1):
                #print bb.inst[idx]
                if bb.inst[idx].addr >= addr:
                    new_bb = basic_block()
                    new_bb.inst = bb.inst[idx:]
                    bb.inst = bb.inst[:idx]
                    append_bb(context, new_bb)
                    #create_edge_by_bb(context, bb, new_bb)
                    return bb, new_bb
            return bb, bb
    return None, None

def create_context():
    return context()

def get_first_bb(context):
    return context.bbs[0]

def get_predcessors(context, bb):
    result = []
    for edge in context.edges:
        if edge.to_bb == bb:
            result.append(edge.from_bb)
    return result

def get_successors(context, bb):
    result = []
    for edge in context.edges:
        if edge.from_bb == bb:
            result.append(edge.to_bb)
    return result

def lookup_bfs_internal(context, bb, functor, param, visited):
    if bb in visited:
        return
    visited += [bb]

    succcessors = get_successors(context, bb)
    for s in succcessors:
        if not s in visited:
            functor(context, s, param)
        
    for s in succcessors:
        if not s in visited:
            lookup_bfs_internal(context, s, functor, param, visited)

def lookup_bfs(context, functor, param):
    start_point = get_first_bb(context)
    functor(context, start_point, param)
    visited = []
    lookup_bfs_internal(context, start_point, functor, param, visited)

def lookup_reverse_dfs_internal(context, bb, functor, param, visited):
    if not functor(context, bb, param):
        #print 'Exit at:',bb
        return
    predcessors = get_predcessors(context, bb)
    #print 'predcessors:', ",".join(['%s' % x for x in predcessors])
    visited += [bb]
    for p in predcessors:
        if not p in visited:
            lookup_reverse_dfs_internal(context, p, functor, param, visited)

def lookup_reverse_dfs(context, start_point, functor, param):
    visited = []
    lookup_reverse_dfs_internal(context, start_point, functor, param, visited)
