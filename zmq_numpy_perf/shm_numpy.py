import math
import time

import numpy as np

def main():
    begin = time.time()
    niter = 100
    size = 1024 * 1024 * 128
    for i in range(niter):
        a = np.arange(size)
        a = 1
    elapse = time.time() - begin
    print('\nTest malloc performance')
    print('*' * 32)
    print('size = %d' % (size * 8))
    print('niter = %d' % niter)
    print('elapse = %f' % elapse)
    print('iteration / second = %f' % (niter/elapse))
    print('second / iteration = %f' % (elapse/niter))

    size = 1024 * 1024 * 4
    a = np.arange(size).reshape(int(math.sqrt(size)), int(math.sqrt(size)))
    b = np.arange(size).reshape(int(math.sqrt(size)), int(math.sqrt(size)))
    niter = 10
    begin = time.time()
    for i in range(niter):
        c = np.dot(a, b)
    elapse = time.time() - begin
    print('\nTest computation performance on different memory type')
    print('*' * 32)
    print('size = %d' % (size * 8))
    print('niter = %d' % niter)
    print('elapse = %f' % elapse)
    print('iteration / second = %f' % (niter/elapse))
    print('second / iteration = %f' % (elapse/niter))


if __name__ == '__main__':
    main()
