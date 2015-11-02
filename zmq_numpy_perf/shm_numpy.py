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
    print('Test malloc performance')
    print('size = %d' % size * 8)
    print('niter = %d' % niter)
    print('elapse = %f' % elapse)
    print('iteration / second = %f' % (elapse / niter))

    a = np.arange(1024 * 1024 * 64).reshape(1024 * 8, 1024 * 8)
    b = np.arange(1024 * 1024 * 64).reshape(1024 * 8, 1024 * 8)
    for i in range(niter):
        c = np.dot(a, b)
    print('Test computation performance on different memory type')
    print('size = %d' % size * 8)
    print('niter = %d' % niter)
    print('elapse = %f' % elapse)
    print('iteration / second = %f' % (elapse / niter))


if __name__ == '__main__':
    main()
