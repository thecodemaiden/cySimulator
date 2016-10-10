import re
import numpy
from scipy.io import savemat
from collections import defaultdict
import sys 

patt = r'Geophone(\d).*?(\d+\.\d+)\t(\d+\.\d+(e[+-]\d+)?)'

extracted = defaultdict(list) # by time

with open('shijia_exp.log') as infile:
    for line in infile:
        m = re.search(patt, line)
        if m is not None:
            found = m.groups()
            vals = (int(found[0]), float(found[1]), float(found[2]))
            #print m.groups()
            extracted[vals[1]].append(vals)

# now process
arr = numpy.ndarray([5, len(extracted)], dtype=float)

properTime = sorted(extracted.keys())
i = 0
for t in properTime:
    vList = extracted[t]
    arr[0][i] = t
    for v in vList:
        idx = v[0]
        arr[idx][i] = v[2]
    i+=1

if len(sys.argv) == 1:
    filename = 'shijia_sim.mat'
else:
    filename = sys.argv[1]

savemat(filename, {'sim_data':arr})
