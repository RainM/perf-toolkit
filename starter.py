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

import argparse

import cfg_types


module_names = ['phase_disassembler', 'phase_extract_loops', 'phase_graphviz']

def main():
    modules = [__import__(x) for x in module_names]
    [x.init() for x in modules]
    parser = argparse.ArgumentParser()
    [x.init_argparser(parser) for x in modules]
    context = cfg_types.create_context()
    context.options = parser.parse_args()
    [x.apply_options(context.options) for x in modules]
    print '-------------------'
    for x in modules:
        print 'Run -> %s' % (x.get_name())
        if not x.do_phase(context):
            print 'FAIL'
            return
        print 'OK'
        print '-------------------'

if __name__ == '__main__':
    main()
