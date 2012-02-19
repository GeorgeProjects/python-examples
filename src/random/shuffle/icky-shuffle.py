# -*- coding: utf-8 -*-
# ex: set ts=4 et:

"""
Ryan Flynn <parseerror@gmail.com> github.com/rflynn

Challenge: http://beust.com/weblog/2012/02/16/a-new-coding-challenge-2/
1) A function which, passed an int n, returns an array of size n containing
   all the numbers between 0 and n-1 in random order.
   For example, with n=5, valid answers are [0,2,3,1,4], [4,1,2,0,3], etc…
2) Prove that the function you wrote in 1) returns “really random” arrays.

Reasoning:
 The distinct outputs for shuffling [1..n] are n!
 Given a random ordering the probability of any one number appearing in a
 particular position is 1/n.
 Therefore, we can estimate the effectiveness of the entire shuffle by running
 many trials and measuring the frequency of the [0]th element.
"""

import scipy
import random
from array import array

def seqshuffle(n):
    seq = array('L', range(n))
    random.shuffle(seq)
    return seq

if __name__ == '__main__':

    from multiprocessing import Manager, Queue, Pool
    from math import ceil
    import time
    import sys

    def run(args):
        # [0]th value frequency over a set of trials
        n, size, runs, q = args
        start = time.time()
        v = array('L', [0 for x in range(size)])
        for _ in xrange(runs):
            try:
                v[seqshuffle(size)[0]] += 1
            except KeyboardInterrupt:
                continue
        now = time.time()
        q.put((n, size, runs, v, now - start))

    MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    RUNS = range(1, 20)

    man = Manager()
    q = man.Queue()
    p = Pool()
    trials = [(n, MAX, (n*20)**2, q) for n in RUNS]
    p.map_async(run, trials)

    # blame http://zachseward.com/sparktweets/
    # http://en.wikipedia.org/wiki/List_of_Unicode_characters#Block_elements
    BLOCKS = u' _▁▂▃▄▅▆▇█'

    try:
        for r in RUNS:
            # laziest way of displaying results in the right order
            n = None
            while n != r:
                n, size, runs, v, elapsed = q.get()
                if n != r:
                    q.put((n, size, runs, v, elapsed))
            # print header occasionally
            if n % 25 == 1:
                print '%-5s %-4s %-6s %-4s %-4s %-6s %s' % (
                    'secs', 'n', 'trials', 'mean', 'std', 'var', 'graph')
            # dump stats
            mean = scipy.mean(v)
            std = scipy.std(v)
            outside = max(abs(x-mean) for x in v)
            dist = outside / (1 if std == 0 else std)
            print '%5.1f %4u %6s %4u %4.1f %6.1f ' % (
                elapsed, size, runs, mean, std, scipy.var(v)),
            # silly Unicode histogram
            maxv = max(v)
            for k,freq in enumerate(v):
                scale = float(freq) / maxv
                b = int(ceil(len(BLOCKS) * scale))
                sys.stdout.write(BLOCKS[b-1])
            sys.stdout.write('\n')
    except KeyboardInterrupt:
        try:
            p.terminate()
        except:
            pass

