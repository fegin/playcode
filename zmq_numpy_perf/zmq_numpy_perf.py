from __future__ import print_function
import argparse
import threading
import time 

import numpy as np
import zmq


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


class ZmqTestModule(object):
    ZMQ_TYPE_INPROC = 1
    ZMQ_TYPE_IPC = 2
    ZMQ_TYPE_TCP = 3

    def __init__(self, context, ztype, niter, array_shape):
        self.context = context
        
        zmq_addr = {ZMQ_TYPE_INPROC: 'inproc://TestModule.inproc',
                    ZMQ_TYPE_IPC: 'ipc://TestModule.ipc',
                    ZMQ_TYPE_TCP: 'tcp://*:5555'}

        self.srv_socket = context.socket(zmq.REP)
        self.cli_socket = context.socket(zmq.REQ)
        self.srv_socket.bind(zmq_addr[ztype])
        self.cli_socket.connect(zmq_addr[ztype])
        self.srv_thread = threading.Thread(target=self.server, 
                                           args=(niter,))
        self.cli_thread = threading.Thread(target=self.client, 
                                           args=(niter, array_shape,))

    def run(self):
        self.srv_thread.start()
        self.cli_thread.start()

    def join(self):
        self.srv_thread.join()
        self.cli_thread.join()

    def server(self, niter):
        for i in range(niter):
            msg = recv_array(self, self.srv_socket, copy=False)
            self.srv_socket.send(b"World")

        self.srv_socket.close()

    def client(self, niter, array_shape):
        array = np.arange(reduce(lambda x, y: x * y, array_shape)
                         ).reshape(array_shape)

        begin = time.time()
        for i in range(niter):
            send_array(self, self.cli_socket, array, copy=False)
            msg = self.cli_socket.recv()
        elapse = time.time() - begin

        print('Iteration per second :', niter / elapse, '\n',
              'Throughput (MBps) :', (niter * array.nbytes / elapse 
                                      / 1024 / 1024))

        self.cli_socket.close()

    def send_array(self, socket, A, flags=0, copy=True, track=False):
        """send a numpy array with metadata"""
        md = dict(dtype=str(A.dtype), shape=A.shape)
        socket.send_json(md, flags | zmq.SNDMORE)
        return socket.send(A, flags, copy=copy, track=track)

    def recv_array(self, socket, flags=0, copy=True, track=False):
        """recv a numpy array"""
        md = socket.recv_json(flags=flags)
        msg = socket.recv(flags=flags, copy=copy, track=track)
        buf = buffer(msg)
        A = np.frombuffer(buf, dtype=md['dtype'])
        return A.reshape(md['shape'])


def main():
    # parser = argparse.ArgumentParser(prog="zmq_numpy_perf")

    context = zmq.Context.instance()

    array_shape = (1024, 1024)

    gil_test = GilTestModule(GilTestModule.BUSYLOOP_PYTHON, 2048*2048, 4, array_shape)
    gil_test.run()
    gil_test.join()
    gil_test = GilTestModule(GilTestModule.BUSYLOOP_NUMPY, 5, 4, array_shape)
    gil_test.run()
    gil_test.join()

if __name__ == '__main__':
    main()
