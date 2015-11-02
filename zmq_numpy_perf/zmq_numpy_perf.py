from __future__ import print_function
import argparse
import threading
import multiprocessing
import time 

import numpy as np
import zmq
import cPickle


class GilTestModule(object):
    BUSYLOOP_PYTHON = 1
    BUSYLOOP_NUMPY = 2

    def __init__(self, btype, niter, nthread, array_shape):
        args = (btype, niter, nthread, array_shape)
        self.test_thread = threading.Thread(target=self.test, args=args)
                                            
    def run(self):
        self.test_thread.start()

    def test(self, btype, niter, nthread, array_shape):
        threads1 = []
        threads2 = []
        if btype == self.BUSYLOOP_PYTHON:
            print('\nBUSYLOOP_PYTHON', '-' * 32, sep='\n')
            for i in range(nthread):
                threads1.append(threading.Thread(target=self.busyloop_python,
                                                 args=(niter,)))
                threads2.append(threading.Thread(target=self.busyloop_python,
                                                 args=(niter,)))
        elif btype == self.BUSYLOOP_NUMPY:
            print('\nBUSYLOOP_NUMPY', '-' * 32, sep='\n')
            for i in range(nthread):
                threads1.append(threading.Thread(target=self.busyloop_numpy,
                                                 args=(niter, array_shape)))
                threads2.append(threading.Thread(target=self.busyloop_numpy,
                                                 args=(niter, array_shape)))
        begin = time.time()
        _ = [t.start() for t in threads1]
        _ = [t.join() for t in threads1]
        elapse = time.time() - begin
        print('Spent %f to finish %d niter in %d threads' % 
              (elapse, niter * nthread, nthread))

        begin = time.time()
        _ = [t.start() or t.join() for t in threads2]
        elapse2 = time.time() - begin
        print('Spent %f to finish %d niter' % (elapse2, niter * nthread))

        print('Scalability', elapse2 / elapse, 'thread number', nthread)

    def join(self):
        self.test_thread.join()

    def busyloop_python(self, niter):
        a = 1
        for i in range(niter):
            a = (1739 * a - 1238 + a) % 137

    def busyloop_numpy(self, niter, array_shape):
        total = reduce(lambda x, y: x * y, array_shape)
        
        a = np.arange(total).reshape(array_shape)
        b = np.arange(total).reshape(array_shape)
        for i in range(niter):
            c = np.dot(a, b)


def send_header_json(socket, flags=0):
    md = dict(dtype=str('int64'), shape=(1000 * 1000, 1000 * 1000))
    return socket.send_json(md, flags)


def recv_header_json(socket, flags=0):
    return socket.recv_json(flags)


def send_header_cpickle(socket, flags=0, copy=True):
    md = dict(dtype=str('int64'), shape=(1000 * 1000, 1000 * 1000))
    md = cPickle.dumps(md)
    return socket.send(md, flags , copy=copy)


def recv_header_cpickle(socket, flags=0, copy=True):
    md = socket.recv(flags, copy=copy)
    md  = cPickle.loads(str(md))
    return md


def send_array_json(socket, A, flags=0, copy=True):
    md = dict(dtype=str(A.dtype), shape=A.shape)
    socket.send_json(md, flags | zmq.SNDMORE)
    return socket.send(A, flags, copy=copy)


def recv_array_json(socket, flags=0, copy=True):
    md = socket.recv_json(flags)
    msg = socket.recv(flags=flags, copy=copy)
    buf = buffer(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])


def send_array_cpickle(socket, A, flags=0, copy=True):
    md = dict(dtype=str(A.dtype), shape=A.shape)
    md = cPickle.dumps(md)
    socket.send(md, flags | zmq.SNDMORE, copy=True)
    return socket.send(A, flags, copy=copy)


def recv_array_cpickle(socket, flags=0, copy=True):
    md = socket.recv(flags, copy=True)
    md  = cPickle.loads(str(md))
    msg = socket.recv(flags=flags, copy=copy)
    buf = buffer(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])


def test_srv_wrapper(func):
    def f(niter, size, addr, copy, sock=None):
        if not sock:
            sock = zmq.Context().socket(zmq.REP)
            sock.bind(addr)
        func(niter, size, addr, copy, sock)
        time.sleep(1.5)
        sock.close()
    return f


def test_cli_wrapper(func):
    def f(niter, size, addr, copy, sock=None):
        if not sock:
            sock = zmq.Context().socket(zmq.REQ)
            sock.connect(addr)
        print('Start Client')
        begin = time.time()
        func(niter, size, addr, copy, sock)
        elapse = time.time() - begin
        print('Address', ':', addr)
        print('Size', ':', size)
        print('Copy', ':', copy)
        print('niter', ':', niter)
        print('Latency', ':', str(elapse / niter * 1e6), 'us')
        print('Iterations per second', ':', niter / elapse)
        print('Throughput per second(Mbps)', ':', 
              size * 2 * niter * 8.0 / elapse / 1024 / 1024)
        print('Elapse', ':', elapse)
        sock.close()
    return f


def test_wrapper(func):
    def f(*args, **kwargs):
        print('')
        print(func.__name__)
        print('-' * 32)
        func(*args, **kwargs)
    return f


@test_wrapper
def test_header_json(niter, size, addr, copy):
    @test_srv_wrapper
    def test_srv(niter, size, addr, copy, sock=None):
        for i in xrange(niter):
            msg = recv_header_json(sock)
            send_header_json(sock)
            
    @test_cli_wrapper
    def test_cli(niter, size, addr, copy, sock=None):
        for i in xrange(niter):
            send_header_json(sock)
            msg = recv_header_json(sock)

    srv = multiprocessing.Process(target=test_srv, args=(niter, size, addr, copy))
    cli = multiprocessing.Process(target=test_cli, args=(niter, size, addr, copy))
    srv.start()
    cli.start()
    srv.join()
    cli.join()


@test_wrapper
def test_header_cpickle(niter, size, addr, copy):
    @test_srv_wrapper
    def test_srv(niter, size, addr, copy, sock=None):
        for i in xrange(niter):
            msg = recv_header_cpickle(sock, copy=copy)
            send_header_cpickle(sock, copy=copy)
            
    @test_cli_wrapper
    def test_cli(niter, size, addr, copy, sock=None):
        msg = np.arange(size / 4, dtype=np.int32).reshape((size / 4, 1))
        for i in xrange(niter):
            send_header_cpickle(sock, copy=copy) 
            msg = recv_header_cpickle(sock, copy=copy)

    srv = multiprocessing.Process(target=test_srv, args=(niter, size, addr, copy))
    cli = multiprocessing.Process(target=test_cli, args=(niter, size, addr, copy))
    srv.start()
    cli.start()
    srv.join()
    cli.join()


@test_wrapper
def test_array_json(niter, size, addr, copy):
    @test_srv_wrapper
    def test_srv(niter, size, addr, copy, sock=None):
        for i in xrange(niter):
            msg = recv_array_json(sock, copy=copy)
            send_array_json(sock, msg, copy=copy)
            
    @test_cli_wrapper
    def test_cli(niter, size, addr, copy, sock=None):
        msg = np.arange(size / 4, dtype=np.int32).reshape((size / 4, 1))
        for i in xrange(niter):
            send_array_json(sock, msg, copy=copy) 
            msg = recv_array_json(sock, copy=copy)

    srv = multiprocessing.Process(target=test_srv, args=(niter, size, addr, copy))
    cli = multiprocessing.Process(target=test_cli, args=(niter, size, addr, copy))
    srv.start()
    cli.start()
    srv.join()
    cli.join()


@test_wrapper
def test_array_cpickle(niter, size, addr, copy):
    @test_srv_wrapper
    def test_srv(niter, size, addr, copy, sock=None):
        for i in xrange(niter):
            msg = recv_array_cpickle(sock, copy=copy)
            send_array_cpickle(sock, msg, copy=copy)
            
    @test_cli_wrapper
    def test_cli(niter, size, addr, copy, sock=None):
        msg = np.arange(size / 4, dtype=np.int32).reshape((size / 4, 1))
        for i in xrange(niter):
            if i == niter - 1:
                print ('Almost Done')
            send_array_cpickle(sock, msg, copy=copy) 
            if i == niter - 1:
                print ('Should be done')
            msg = recv_array_cpickle(sock, copy=copy)
            if i == niter - 1:
                print ('Should be done')

    srv = multiprocessing.Process(target=test_srv, args=(niter, size, addr, copy))
    cli = multiprocessing.Process(target=test_cli, args=(niter, size, addr, copy))
    srv.start()
    cli.start()
    srv.join()
    cli.join()


@test_wrapper
def test_msg(niter, size, addr, copy):
    @test_srv_wrapper
    def test_srv(niter, size, addr, copy, sock=None):
        for i in xrange(niter):
            msg = sock.recv(copy=copy)
            sock.send(msg, copy=copy)

    @test_cli_wrapper            
    def test_cli(niter, size, addr, copy, sock=None):
        msg = b'0' * size
        for i in xrange(niter):
            sock.send(msg, copy=copy)
            msg = sock.recv(copy=copy)

    srv = multiprocessing.Process(target=test_srv, args=(niter, size, addr, copy))
    cli = multiprocessing.Process(target=test_cli, args=(niter, size, addr, copy))
    srv.start()
    cli.start()
    srv.join()
    cli.join()


def main():
    # parser = argparse.ArgumentParser(prog="zmq_numpy_perf")

    context = zmq.Context.instance()

    niter = 2**17
    for size in tuple(2 ** i for i in range(25)):
        niter_ = niter
        if size >= 2 ** 21:
            niter_ /= size / (2 ** 20)
        print (size, niter_)
        test_msg(niter_, size, "ipc://localhost.ipc", True)
        test_msg(niter_, size, "tcp://127.0.0.1:5555", True)
        test_msg(niter_, size, "ipc://localhost.ipc", False)
        test_msg(niter_, size, "tcp://127.0.0.1:5555", False)

    test_header_cpickle(niter, 1, "ipc://localhost.ipc", True)
    test_header_cpickle(niter, 1, "tcp://127.0.0.1:5555", True)
    test_header_cpickle(niter, 1, "ipc://localhost.ipc", False)
    test_header_cpickle(niter, 1, "tcp://127.0.0.1:5555", False)
    test_header_json(niter, 1, "ipc://localhost.ipc", True)
    test_header_json(niter, 1, "tcp://127.0.0.1:5555", True)

    for size in tuple(2 ** i for i in range(25)):
        niter_ = niter
        if size >= 2 ** 21:
            niter_ /= size / (2 ** 20)
        test_array_json(niter_, size, "ipc://localhost.ipc", True)
        test_array_json(niter_, size, "tcp://127.0.0.1:5555", True)
        test_array_json(niter_, size, "ipc://localhost.ipc", False)
        test_array_json(niter_, size, "tcp://127.0.0.1:5555", False)
        test_array_cpickle(niter_, size, "ipc://localhost.ipc", True)
        test_array_cpickle(niter_, size, "tcp://127.0.0.1:5555", True)
        test_array_cpickle(niter_, size, "ipc://localhost.ipc", False)
        test_array_cpickle(niter_, size, "tcp://127.0.0.1:5555", False)


if __name__ == '__main__':
    main()
