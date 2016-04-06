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

from functools import partial

import cfg_types


def dominator_functor(context, bb, dominators):
    print "Dominator:", bb
    predcessors = cfg_types.get_predcessors(context, bb)
    if len(predcessors) == 0:
        dominators[bb] = set([bb])
        return
    current_dominators = set(cfg_types.all_bbs(context))
    for p in predcessors:
        print "\tPredcessor:", p
        if p in dominators:
            #print ",".join(['%s' % x for x in dominators[p]])
            current_dominators = set(dominators[p]).intersection(set(current_dominators))
    current_dominators.add(bb)
    dominators[bb] = current_dominators
    #print 'Dominators:', ",".join(['%s' % x for x in dominators[bb]])

def calculate_dominators(context):
    result = {}
    first_bb = cfg_types.get_first_bb(context)
    if not first_bb in result:
        result[first_bb] = []
    
    result[first_bb].append(first_bb)
    
    cfg_types.lookup_bfs(context, dominator_functor, result)

    return result

def calculate_reverse_backedges(context, dominators):
    result = []
    for e in cfg_types.all_edges(context):
        if e.from_bb not in dominators:
            print 'Edge:', e
            print 'no dominators for FROM:', e.from_bb
            continue
        if e.to_bb not in dominators:
            print 'Edge:', e
            print 'no dominators for TO:  ', e.to_bb
            continue
        dominators_from = dominators[e.from_bb]
        dominators_to   = dominators[e.to_bb]
        #print 'BackEdge:', e
        #print 'FromBB:', e.from_bb
        #print 'ToBB:', e.to_bb
        #print 'FromDominators:', ",".join(['%s' % x for x in dominators_from])
        #print 'ToDominators:', ",".join(['%s' % x for x in dominators_to])
        if not (dominators_to > dominators_from):
            #print 'Decision: true'
            result.append(e)
        #else:
        #    #print 'Decision: false'
    return result

def calculate_single_loop(last_bb, context, bb, param):
    #print 'reverse dfs:', bb
    param += [bb]
    if last_bb == bb:
        #print 'False'
        return False
    return True

def calculate_loops(context, back_edges):
    #print 'Loops'
    result = []
    for e in back_edges:
        bbs_loop = []
        functor = partial(calculate_single_loop, e.to_bb)
        print 'BackEdge:', e
        cfg_types.lookup_reverse_dfs(context, e.from_bb, functor, bbs_loop)
        print "\t" + "\n\t".join(['%s' % x for x in bbs_loop])
        #l = cfg_types.loop()
        #l.bbs = bbs_loop
        #result.append(l)
        result.append(bbs_loop)
    return result

def merge_loops(context, loops):
    loops_in_bb = {}
    
    for loop in loops:
        for bb in loop.bbs:
            if not bb in loops_in_bb:
                loops_in_bb[bb] = [loop]
            else:
                loops_in_bb[bb] += [loop]
    #print loops_in_bb
    loops_to_merge = []
    result = []

    while len(loops_in_bb.keys()) > 0:
        bb, loops = loops_in_bb.popitem()
        for loops_per_bb in loops_in_bb.itervalues():
            should_merge = False
            for l in loops_per_bb:
                if l in loops:
                    should_merge = True
                    break
            if should_merge:
                for l in loops_per_bb:
                    if l not in loops:
                        loops += [l]
        # so, loops contains all loops for bb
        # now, we should create a new big loop (for all loops) and 
        # move all applicable bbs to the new loop
        #print 'Loops to merge'
        #print "\n".join(['%s' % x for x in loops])
        new_big_loop = cfg_types.loop()
        for loop in loops:
            for bb in loop.bbs:
                if bb not in new_big_loop.bbs:
                    new_big_loop.bbs += [bb]
        #print 'New loop:'
        #print '%s' % new_big_loop
        for bb in new_big_loop.bbs:
            if bb in loops_in_bb:
                del loops_in_bb[bb]
        new_big_loop.bbs += [bb]
        result.append(new_big_loop)

    #print 'Loops to merge:'
    #print "\t" + "\n\t".join(['%s' % x for x in result])
    return result

def init_argparser(argparser):
    argparser.add_argument('--loops', dest='loops', action='store_true', default=False)
    argparser.add_argument('--no-merge-loops', dest='no_merge_loops', action='store_true', default=False)

def init():
    pass

def apply_options(options):
    pass

def get_name():
    return "phase_extract_loop"

def do_phase(context):
    if not context.options.loops:
        return True
    dominators = calculate_dominators(context)
    for k in dominators.keys():
        print k
        print "\t" + "\n\t".join(['%s' % x for x in dominators[k]])
    backedges = calculate_reverse_backedges(context, dominators)
    print 'Backedges:'
    print "\n".join(['%s' % x for x in backedges])
    loops = calculate_loops(context, backedges)
    for bbs in loops:
        loop = cfg_types.loop()
        loop.bbs = bbs
        context.loops.append(loop)

    if not context.options.no_merge_loops:
        context.loops = merge_loops(context, context.loops)
        
    return True
