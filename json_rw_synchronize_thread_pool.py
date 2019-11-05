import threading
import time
import json


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
        super(sync_pool, self).__init__()

    def action(self, do, data=None):
        allocated = 0
        while allocated == 0:
            for thread_id in self.sync_sample.keys():
                if self.sync_sample[thread_id] is None or not self.sync_sample[thread_id].mutex:
                    alloc_pool = thread_id
                    allocated = 1
                    break
        self.sync_sample[alloc_pool] = sync_sample(alloc_pool, self.evt, mutex=True,)
        self.sync_sample[alloc_pool].mode = do
        self.sync_sample[alloc_pool].data = data
        self.sync_sample[alloc_pool].start()
        #self.evt.wait()

    def end_pool(self):
        self.end_flag = False

    def run(self):
        while self.end_flag:
            pass

class operation():

    def __init__(self, filename):
        pass

    def read(self):
        with open(self.track) as json_file:
                data = json.load(json_file)

    def write(self):
        pass

    def update(self):
        pass


class rw_thread(threading.Thread):

    def __init__(self, thread_number, evt, mutex=False):
        self.thread_number = thread_number
        self.class_data = None
        self.mutex = mutex
        self.evt = evt
        self.evt.set()
        super(sync_sample, self).__init__()

    def __enter__(self):
        self.evt.clear()
        for i in range(10):
            time.sleep(1)
        return self.class_data
        
    def __exit__(self, exception_type, exception_value, traceback):
        self.class_data = self.data
        for i in range(10):
            time.sleep(1)
        self.evt.set()


    def sync_write(self):
        self.evt.clear()
        self.class_data = self.data
        for i in range(10):
            time.sleep(1)
        self.evt.set()


    def read(self):
        if not self.evt.is_set():
            self.evt.wait()
        for i in range(10):
            time.sleep(1)
        print self.class_data

    def run(self):
        self.mutex = True
        print "Thread id: {}, data: {}, operation: {}".format(self.thread_number, self.data, self.mode)
        if self.mode == "read":
            self.read()
        elif self.mode == "write":
            self.sync_write()
        elif self.mode == "rw":
            with self as chunk:
                print chunk
        else:
            print "no operation"
        print "Ending thread number: {}, iter: {}".format(self.thread_number, self.data)
        self.mutex = False

if __name__ == "__main__":
    '''
    pool_1 = pool(100)
    #pool_1.start()
    mode = ["read", "write"]
    for i in range(200):
        pool_1.action( mode[i%2], "this is operation {}, iteration {}".format(mode[i%2], i) )
    '''


    sync_pool_1 = sync_pool(100)

    sync_mode = ["read", "write", "rw"]
    for i in range(200):
        sync_pool_1.action( sync_mode[i%3], "thia ia operation {}, iteration {}".format(sync_mode[i%3], i) )

