import math
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

data_type = {'msg' : 'raw', 'header' : 'header', 'array' : 'array'}
data_protocol = {'tcp' : 'tcp', 'ipc' : 'ipc'}
data_copy = {True : 'copy', False : 'notcopy'}
data_method = {'json' : 'json', 'cpickle' : 'cPickle'}

data = {'msg': {}, 'header': {}, 'array': {}}

with open('log') as fp:
    begin = False
    #dtype = None
    #method = None
    #size = 0
    #is_copy = False
    #niter = 0
    #latency = 0
    #iterations = 0
    #throughput = 0
    for line in fp:
        line = line.strip()
        if line.startswith('test_'):
            begin = True
            words = line.split('_')
            dtype = words[1]
            if words[1] == 'msg':
                method = None
            else:
                method = words[2]
        elif begin:
            words = line.split()
            if words[0] == 'Address':
                if words[2].find('ipc') >= 0:
                    protocol = 'ipc' 
                elif words[2].find('tcp') >= 0:
                    protocol = 'tcp'
                    begin = False
                else:
                    raise Exception
            elif words[0] == 'Size':
                size = math.log(int(words[2]), 2)
                #size = int(words[2])
            elif words[0] == 'Copy':
                is_copy = eval(words[2])
            elif words[0] == 'niter':
                niter = int(words[2])
            elif words[0] == 'Latency':
                latency = float(words[2])
            elif words[0] == 'Iterations':
                iterations = float(words[4])
            elif words[0] == 'Throughput':
                throughput = float(words[4])
            elif words[0] == 'Elapse':
                begin = False
                name = data_type[dtype] + '_' + data_protocol[protocol]
                if method:
                    name += '_' + data_method[method]
                name += '_' + data_copy[is_copy]
                if not data[dtype].get(name, None):
                    data[dtype][name] = {}
                data[dtype][name][size] = [latency, iterations, throughput]


for dtype in data.keys():
    throughput = {}
    latency = {}
    iterations = {}
    for name, val in data[dtype].items():
        size = val.keys()
        size.sort()
        latency[name]    = [size, [val[s][0] for s in size]]
        iterations[name] = [size, [val[s][1] for s in size]]
        throughput[name] = [size, [val[s][2] for s in size]]

    for name, val in latency.items():
        plt.plot(val[0], val[1], 'o--', label=name)
    plt.grid(True)
    plt.xlabel('Size (log(bytes), normalized)')
    plt.ylabel('Latency (us)')
    legend = plt.legend(loc='upper left', shadow=True)
    inset_axes(plt.axes(), width="45%", height="45%", loc=10)
    for name, val in latency.items():
        plt.plot(val[0][:17], val[1][:17], 'o--', label=name)
    plt.grid(True)
    plt.show()
    plt.cla()

    for name, val in iterations.items():
        plt.plot(val[0], val[1], 'o--', label=name)
    legend = plt.legend(loc='upper right', shadow=True)
    plt.grid(True)
    plt.xlabel('Size (log(bytes), normalized)')
    plt.ylabel('Iterations')
    plt.show()
    plt.cla()

    for name, val in throughput.items():
        plt.plot(val[0], val[1], 'o--', label=name)
    legend = plt.legend(loc='upper left', shadow=True)
    plt.grid(True)
    plt.xlabel('Size (log(bytes), normalized)')
    plt.ylabel('Throughput (MBps)')
    plt.show()
    plt.cla()

