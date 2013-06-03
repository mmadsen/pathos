#!/usr/bin/env python

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
# 
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials
#       provided with the distribution.
# 
#     * Neither the name of Kirk Strauser nor the names of other
#       contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# (also see code fork in pathos.pp)

"""
Very basic parallel processing support

Implements a work-alike of the builtin map() function that distributes
work across many processes.  As it uses Parallel Python to do the
actual multi-processing, code using this must conform to the usual PP
restrictions (arguments must be serializable, etc.)
"""

from pathos.pp import __STATE, stats, __print_stats as print_stats
#from pathos.pp import ParallelPythonPool as Pool
from pathos.helpers.pp_helper import Server as ppServer


def ppmap(processes, function, sequence, *sequences):
    """Split the work of 'function' across the given number of
    processes.  Set 'processes' to None to let Parallel Python
    autodetect the number of children to use.

    Although the calling semantics should be identical to
    __builtin__.map (even using __builtin__.map to process
    arguments), it differs in that it returns a generator instead of a
    list.  This enables lazy evaluation of the results so that other
    work can be done while the subprocesses are still running.

    >>> def rangetotal(n): return n, sum(range(n))
    >>> list(map(rangetotal, range(1, 6)))
    [(1, 0), (2, 1), (3, 3), (4, 6), (5, 10)]
    >>> list(ppmap(1, rangetotal, range(1, 6)))
    [(1, 0), (2, 1), (3, 3), (4, 6), (5, 10)]
    """

    ppservers = ("*",) # autodetect
    #from _ppserver_config import ppservers # read from a config file

    # Create a new server if one isn't already initialized
    if not __STATE['server']:
        __STATE['server'] = ppServer(ppservers=ppservers)
    
   #class dill_wrapper(object):
   #    """handle non-picklable functions by wrapping with dill"""
   #    def __init__(self, function):
   #        from dill import dumps
   #        self.pickled_function = dumps(function)
   #    def __call__(self, *args):
   #        from dill import loads #XXX: server now requires dill
   #        f = loads(self.pickled_function) 
   #        return f(*args)

#   def dill_wrapper(function):
#       """handle non-picklable functions by wrapping with dill"""
#       from dill import dumps
#       pickled_function = dumps(function)
#       def unwrap(*args):
#           from dill import loads #XXX: server now requires dill
#           f = loads(pickled_function) 
#           return f(*args)
#       return unwrap

    def submit(*args): #XXX: needs **kwds to allow "depfuncs, modules, ...?
        """Send a job to the server"""
       #print globals()['ncalls'] #FIXME: ncalls not in globals()
       #XXX: options for submit...
       #XXX: func -- function to be executed
       #XXX: depfuncs -- functions called from 'func'
       #XXX: modules -- modules to import
       #XXX: callback -- callback function to be called after 'func' completes
       #XXX: callbackargs -- additional args for callback(result, *args)
       #XXX: group -- allows naming of 'job group' to use in wait(group)
       #XXX: globals -- dictionary from which everything imports
#       from mystic.tools import wrap_function, wrap_bounds
#       return __STATE['server'].submit(function, args, \
#              depfuncs=(wrap_function,wrap_bounds), \
##             modules=("mystic","numpy"), \
#              globals=globals())
   #    p_function = dill_wrapper(function)
   #    return __STATE['server'].submit(p_function, args, globals=globals())
       #print __STATE['server'].get_ncpus(), "local workers" #XXX: debug
        return __STATE['server'].submit(function, args, globals=globals())

    # Merge all the passed-in argument lists together.  This is done
    # that way because as with the map() function, at least one list
    # is required but the rest are optional.
    a = [sequence]
    a.extend(sequences)

    # Set the requested level of multi-processing
    #__STATE['server'].set_ncpus(processes or 'autodetect') # never processes=0
    if processes == None:
        __STATE['server'].set_ncpus('autodetect')
    else:
        __STATE['server'].set_ncpus(processes) # allow processes=0
   #print "running with", __STATE['server'].get_ncpus(), "local workers" #XXX: debug

    # First, submit all the jobs.  Then harvest the results as they
    # come available.
    return (subproc() for subproc in map(submit, *a))


def pp_map(function, sequence, *args, **kwds):
    '''extend python's parallel map function to parallel python

Inputs:
    function  -- target function
    sequence  -- sequence to process in parallel

Additional Inputs:
    ncpus     -- number of 'local' processors to use  [defaut = 'autodetect']
    servers   -- available distributed parallel python servers  [default = ()]
    '''
    procs = None
    servers = ()
    if kwds.has_key('ncpus'):
      procs = kwds['ncpus']
      kwds.pop('ncpus')
    if kwds.has_key('servers'):
      servers = kwds['servers']
      kwds.pop('servers')
    # remove all the junk kwds that are added due to poor design!
    if kwds.has_key('nnodes'): kwds.pop('nnodes')
    if kwds.has_key('launcher'): kwds.pop('launcher')
    if kwds.has_key('mapper'): kwds.pop('mapper')
    if kwds.has_key('queue'): kwds.pop('queue')
    if kwds.has_key('timelimit'): kwds.pop('timelimit')
    if kwds.has_key('scheduler'): kwds.pop('scheduler')

#   return Pool(procs, servers=servers).map(function, sequence, *args, **kwds)
    if not __STATE['server']:
        __STATE['server'] = job_server = ppServer(ppservers=servers)
    return list(ppmap(procs,function,sequence,*args))


if __name__ == '__main__':
    # code moved to "pathos/examples/pp_map.py
    pass


# EOF
