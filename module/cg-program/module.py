#
# Collective Knowledge (actions to use with compiler gym)
#
# 
# 
#
# Developer: 
#

cfg = {}  # Will be updated by CK (meta description of this module)
work = {}  # Will be updated by CK (temporal data)
ck = None  # Will be updated by CK (initialized CK kernel)

# Local settings

##############################################################################
# Initialize module


def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return': 0}

##############################################################################
# compiles a given program to bitcode

def compile_to_bitcode(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    import os
    import compiler_gym
    import gym

    # TODO - detect compile deps and run corresponding env.sh files 

    ck.out('Compiles a given program to bitcode')

    # detect platform for various info
    d = {'module_uoa': 'platform.os',
         'action': 'detect'
        }

    r = ck.access(d)
    if r['return']>0: return r
    os_dict = r['os_dict']
    dir_sep = os_dict['dir_sep']


    duoa = i['data_uoa']
    muoa = i['module_uoa']

    # load the entry's dictionary
    d = {'module_uoa': muoa,
         'data_uoa': duoa
        }
    r = ck.load(d)
    if r['return']>0: return r
    path = r['path']
    program_meta = r['dict']

    env_str = program_meta['run_vars']['GYM_ENV']
    # create gym environment
    env = gym.make(env_str)

    program_files = program_meta['source_files']
    env.benchmark = env.make_benchmark(path + dir_sep + program_files[0])
    # init env - do normal env stuff and then measure runtime
    observation = env.reset()
    # write the current program state to a bitcode file
    env.write_bitcode(path + dir_sep + "hello_world.bc")
    # TODO - look at program module to see how they use run_cmd_main from meta to run prgram, do same using clang-10 for bc file
    env.close()

    return {'return':0}

##############################################################################
# run bitcode

def run(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    ck.out('run bitcode')

    ck.out('')
    ck.out('Command line: ')
    ck.out('')

    import json
    cmd=json.dumps(i, indent=2)

    ck.out(cmd)

    return {'return':0}
