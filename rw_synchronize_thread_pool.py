import threading
import time


class rw_pool(threading.Thread):

    sync_sample = {}
    evt = threading.Event()

    # pool with synchronized method

    def __init__(self, max_thread, _file):
        self.max_thread = max_thread
        self.end_flag = True
        self._file = _file
        for i in range(max_thread):
            self.sync_sample[i] = None
        super(rw_pool, self).__init__()

    def action(self, do, data=None):
        allocated = 0
        while allocated == 0:
            for thread_id in self.sync_sample.keys():
                if self.sync_sample[thread_id] is None or not self.sync_sample[thread_id].mutex:
                    alloc_pool = thread_id
                    allocated = 1
                    break
        self.sync_sample[alloc_pool] = rw_thread(alloc_pool, self._file, self.evt, mutex=True,)
        self.sync_sample[alloc_pool].mode = do
        self.sync_sample[alloc_pool].data = data
        self.sync_sample[alloc_pool].start()
        #self.evt.wait()

    def end_pool(self):
        self.end_flag = False

    def run(self):
        while self.end_flag:
            pass

class rw_operation():

    def __init__(self, filename):
        self.filename = filename

    #reading from file
    def op_1(self):
        with open(self.filename, 'r') as f:
            self.data = f.read()

    #writing to file by appending "shad"
    def op_2(self, data):
        with open(self.filename, 'w') as f:
            f.write(self.data + "shad")



class rw_thread(threading.Thread):

    def __init__(self, thread_number, evt, mutex=False):
        self.thread_number = thread_number
        self.class_data = None
        self.mutex = mutex
        self.evt = evt
        self.evt.set()
        super(rw_thread, self).__init__()

    def __enter__(self):
        if not self.evt.is_set():
            self.evt.wait()
        self.evt.clear()

    def __exit__(self, exception_type, exception_value, traceback):
        self.class_data = self.data
        self.evt.set()
        self.ex()


    def read(self):
        if not self.evt.is_set():
            self.evt.wait()

    def run(self):
        self.mutex = True
        print "Thread id: {}, data: {}, operation: {}".format(self.thread_number, self.data, self.mode)
        if self.mode == "read":
            self.read()
        elif self.mode == "write":
            self.sync_write()
        elif self.mode == "multi":
            with self as chunk:
                print chunk
        else:
            print "no operation"
        print "Ending thread number: {}, iter: {}".format(self.thread_number, self.data)
        self.mutex = False

if __name__ == "__main__":

    pool_1 = rw_pool(20, "thread_test.txt")

    mode = ["read", "write", "multi"]

    for i in range(200):
        pool_1.action( mode[i%3], "thia ia operation {}, iteration {}".format(mode[i%3], i) )

