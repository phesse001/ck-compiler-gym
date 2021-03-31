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
import os

##############################################################################
# Initialize module


def init(i):

    import sys 

    path = i['path']

    sys.path.insert(1, path)

    return {'return': 0}

##############################################################################
# compiles a given program to bitcode

def run_dqn(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import subprocess
    import compiler_gym
    import gym
    import time
    import random
    import glob
    import numpy as np
    from dqn import Agent

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

    program_path = r['path']
    program_meta = r['dict']

    program_files = program_meta['source_files']

    for num in range(len(program_files)):
        program_files[num] = program_path + dir_sep + program_files[num]

    env_str = program_meta['run_vars']['GYM_ENV']
    # create gym environment
    env = gym.make(env_str)
    #create benchmark of programs specified with --dataset_tags
    dataset_tags = i['dataset_tags']

    # search for all program entries with specified tags
    d = {'module_uoa': 'program',
         'action': 'search',
         'tags': dataset_tags
        }

    r = ck.access(d)
    if r['return']>0: return r

    # programs is a list of dictionaries containing information about programs matching specified tag
    programs = r['lst']
    # keep track of programs that don't compile
    bad_programs = []

    # check to make sure program compilation is successful before running
    for program in programs:

        program_duoa = program['data_uoa']

        d = {'module_uoa':'program',
             'action': 'compile',
             'compiler_tags': "llvm",
             'data_uoa': program_duoa,
             'use_clang_opt':'yes'
            }

        # compile program to bitcode in tmp dir
        r = ck.access(d)
        
        # for some reason return seems to be 0 even when it fails, using other indicator for now
        # if program compilation fails, remove it from the list of programs to use.
        if r['misc']['compilation_success'] == 'no':

            bad_programs.append(program)

    # remove bad programs
    for program in bad_programs:
        programs.remove(program)

    benchmarks = []

    for program in programs:
        
        program_duoa = program['data_uoa']

        d = {'module_uoa':'program',
             'action': 'load',
             'data_uoa': program_duoa
            }

        # loads programs meta desc
        r = ck.access(d)
        if r['return']>0: return r

        meta = r['dict']
        # find path to program entry
        path = r['path']
        #files = meta['source_files']
        # find out whether entry compiles files to tmp directory
        p_in_tmp = meta['process_in_tmp']
        if p_in_tmp == 'yes':
            path = path + dir_sep + 'tmp'

        # list files in the specified directory and return list of all the bitcode files
        files = [f for f in os.listdir(path) if '.bc' in f]

        for num in range(len(files)):
            files[num] = path + dir_sep + files[num]
        # go through and add path to the start of all the files
        # makes a benchmark with each list of files
        benchmark = env.make_benchmark(files)
        # append tuple of benchmark and uid 
        benchmarks.append((benchmark,meta['backup_data_uid']))


    agent = Agent(gamma = 0.99, epsilon = 1.0, batch_size = 32,
            n_actions = env.action_space.n, eps_end = 0.05, input_dims = [56], alpha = 0.005)

    out = "a"
    ep = os_dict['exec_prefix']
    ext = os_dict['file_extensions']['exe']

    actions = env.action_space.names

    tmp = 0
    for i in range(1,10001):
        benchmark_tuple = random.choice(benchmarks)
        current_benchmark = benchmark_tuple[0]
        data_uoa = benchmark_tuple[1]

        #observation is the 56 dimensional static feature vector from autophase
        observation = env.reset(benchmark=current_benchmark)
        
        done = False
        total = 0
        actions_taken = 0
        agent.actions_taken = []
        # collect data for visualization
        iterations = []
        avg_total = []
        change_count = 0

        while done == False and actions_taken < 100 and change_count < 10:
            #only apply finite number of actions to given program
            action = agent.choose_action(observation)

            new_observation, reward, done, info = env.step(action)
            actions_taken += 1

            total += reward
            if reward == 0:
                change_count += 1
            else:
                change_count = 0

            agent.store_transition(action, observation, reward, new_observation, done)
            agent.learn()
            observation = new_observation
            print("Step " + str(i) + " Cumulative Total " + str(total) +
              " Epsilon " + str(agent.epsilon) + " Action " + str(action) + 
              " No Effect " + str(info))
        tmp += total
        print("avg is " + str(tmp/i))
    
    env.close()
    ck.out('Finished running environment')

    return {'return':0}

##############################################################################
# run bitcode

def run(i):

    tag_grps = ''

    d = {'module_uoa': 'platform.os',
        'action': 'detect'
        }

    r = ck.access(d)
    if r['return']>0: return r
    os_dict = r['os_dict']
    dir_sep = os_dict['dir_sep']

    duoa = i['data_uoa']
    muoa = i['module_uoa']
    dataset_tags = i['dataset_tags']

	# load the entry's dictionary
    d = {'module_uoa': muoa,
        'data_uoa': duoa
        }
    r = ck.load(d)
    if r['return']>0: return r

    program_path = r['path']
    program_meta = r['dict']

	# source env vars for deps... might be better ways to do this
    deps = program_meta['compile_deps']
    for dep,value in deps.items():
        tags = value['tags']
        # create a string of tag groups
        tag_grps += tags + ' '

    d = {'module_uoa':'env',
		 'action': 'virtual',
		 'tag_groups': tag_grps,
		 'shell_cmd': 'ck run_dqn ' + muoa + ':' + duoa + ' --dataset_tags=' + dataset_tags
		}

    r = ck.access(d)
    if r['return']>0: return r

    return {'return':0}

##############################################################################
# creates a dataset of c programs to use within llvm compiler gym env

def make_dataset(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    ck.out('creates a dataset of c programs to use within llvm compiler gym env')

    ck.out('')
    ck.out('Command line: ')
    ck.out('')

    import json
    cmd=json.dumps(i, indent=2)

    ck.out(cmd)

    # TODO 
    # provide repo uoa 
    # 

    return {'return':0}
