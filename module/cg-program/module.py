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

    for program in program_files:
        program = porgram_path + dir_sep + program

    env_str = program_meta['run_vars']['GYM_ENV']
    # create gym environment
    env = gym.make(env_str)
    env.benchmark = env.make_benchmark(program_files)

    agent = Agent(gamma = 0.99, epsilon = 1.0, batch_size = 32,
            n_actions = env.action_space.n, eps_end = 0.05, input_dims = [56], alpha = 0.005)


    bc_file = program_meta['run_cmds']['default']['run_time']['run_cmd_out']
    bc_path = program_path + dir_sep + bc_file
    run_cmd = program_meta['run_cmds']['default']['run_time']['run_cmd_main']
    os.chdir(program_path)

    tmp = 0
    for i in range(1,10001):
        #observation is the 56 dimensional static feature vector from autophase
        observation = env.reset()
        #maybe try setting done to true every time code size increases
        done = False
        total = 0
        actions_taken = 0
        agent.actions_taken = []
        # collect data for visualization
        iterations = []
        avg_total = []
        change_count = 0
        time_old = 0
        #write current observation to bitcode file
        env.write_bitcode(bc_path)
        #compile run and time file bc in original state
        os.system(run_cmd + " " + bc_path)
        # time executable
        os.system('(time ./a.out) &> time.log')
        # read time from file into var
        # runtime = usr + sys time from file

        while done == False and actions_taken < 100 and change_count < 10:
            #only apply finite number of actions to given program
            action = agent.choose_action(observation)
            new_observation, reward, done, info = env.step(action)
            actions_taken += 1
            #run again to see what diff is
            #write current observation to bitcode file
            env.write_bitcode(bc_path)
            #compile run and time file to use runtime as reward signal
            os.system(run_cmd + " " + bc_path)
            # time executable
            os.system('(time ./a.out) &> time.log')
            # TODO - read time from file store into var and compute reward as follows
            # read time from file into var

            # nruntime = usr + sys time from file
            # reward = ln(runtime/nruntime)
            # runtime = nruntime

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
		 'shell_cmd': 'ck run_dqn ' + muoa + ':' + duoa
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

    return {'return':0}
