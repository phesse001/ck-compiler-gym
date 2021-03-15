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

def compile_and_run_bitcode(i):
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
    program_path = r['path']
    program_meta = r['dict']

    env_str = program_meta['run_vars']['GYM_ENV']
    # create gym environment
    env = gym.make(env_str)

    program_files = program_meta['source_files']
    env.benchmark = env.make_benchmark(program_path + dir_sep + program_files[0])
    # init env - do normal env stuff and then measure runtime
    observation = env.reset()
    # write the current program state to a bitcode file
    bc_file = program_meta['run_cmds']['default']['run_time']['run_cmd_out']
    bc_path = program_path + dir_sep + bc_file

    env.write_bitcode(bc_path)
    # TODO - look at program module to see how they use run_cmd_main from meta to run prgram, do same using clang-10 for bc file
    run_cmd = program_meta['run_cmds']['default']['run_time']['run_cmd_main']
    time_cmd = program_meta['run_cmds']['default']['run_time']['time_cmd_main']

    os.chdir(program_path)
    # compile to executable
    subprocess.check_output([run_cmd, bc_file])

    # time executable - TODO - figure out how to record time output
    time = subprocess.check_output([time_cmd, './a.out'])
    
    env.close()

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

	# source env vars for deps... might be better ways to do this via ck api
	deps = program_meta['compile_deps']
	for dep,value in deps.items():
		tags = value['tags']
		# create a string of tag groups
		tag_grps += tags + ' '

	d = {'module_uoa':'env',
		 'action': 'virtual',
		 'tag_groups': tag_grps,
		 'shell_cmd': 'ck compile_and_run_bitcode cg-program:template-hello-world-c'
		}

	r = ck.access(d)
	if r['return']>0: return r

	return {'return':0}
