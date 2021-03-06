#!/usr/bin/env python
"""
example of using the 'raw' distributed parallel mapper

To run: python pp_map.py
"""

from pathos.pp import ParallelPythonPool as Pool
pool = Pool()


if __name__ == '__main__':
    def add(x, y, z):
        """Add three values"""
        return x + y + z

    def busybeaver(x):
        """This can take a while"""
        for num in range(1000000):
            x = x + num
        return x

    # Immediate evaluation example
    import time
    start = time.time()
    results = pool.map(busybeaver, range(10))
    print 'Time to queue the jobs:', time.time() - start
    start = time.time()
    # Casting the ppmap generator to a list forces each result to be
    # evaluated.  When done immediately after the jobs are submitted,
    # our program twiddles its thumbs while the work is finished.
    print list(results)
    print 'Time to get the results:', time.time() - start

    # Delayed evaluation example
    start = time.time()
    results = pool.imap(busybeaver, range(10))
    print 'Time to queue the jobs:', time.time() - start
    # In contrast with the above example, this time we're submitting a
    # batch of jobs then going off to do more work while they're
    # processing.  Maybe "time.sleep" isn't the most exciting example,
    # but it illustrates the point that our main program can do work
    # before ppmap() is finished.  Imagine that you're submitting some
    # heavyweight image processing jobs at the beginning of your
    # program, going on to do other stuff like fetching more work to
    # do from a remote server, then coming back later to handle the
    # results.
    time.sleep(5)
    start = time.time()
    print list(results)
    print 'Time to get the first results:', time.time() - start

    # Built-in map example
    print map(add, [1, 2, 3], [4, 5, 6], [7, 8, 9])

    # Trivial ppmap tests
    for i in range(10):
        print '-' * 30
        start = time.time()
        print pool.map(add, [1, 2, 3], [4, 5, 6], [7, 8, 9])
        print 'Iteration time:', time.time() - start

    # Heavier ppmap tests
    for i in range(10):
        print '-' * 30
        start = time.time()
        print pool.map(busybeaver, range(10))
        print 'Iteration time:', time.time() - start

