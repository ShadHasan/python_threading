import threading
import time
import logging


class rw_pool(threading.Thread):

    rw_threads = {}
    evt = threading.Event()
    gen_thread_id = 0
    thread_buffer = {}

    # pool with synchronized method
    def __init__(self, max_thread, _file):
        self.max_thread = max_thread
        self.end_flag = True
        self._file = _file
        self.evt.set()
        for i in range(max_thread):
            self.rw_threads[i] = None
        super(rw_pool, self).__init__()

    def action(self, do, data=None, operation=None):
        # Thread limit can sorted by initializing gen_thread_id by zero and reallocation by incremental iteration if it is not exist in thread_buff
        self.gen_thread_id = self.gen_thread_id + 1
        
        allocated = 0
        while allocated == 0:
            for pool_num in self.rw_threads.keys():
                if self.rw_threads[pool_num] is None or not self.rw_threads[pool_num].mutex:
                    alloc_pool = pool_num
                    allocated = 1
                    break

        self.rw_threads[alloc_pool] = rw_thread(self.gen_thread_id, self.evt, self._file, mutex=True,)
        self.rw_threads[alloc_pool].mode = do
        self.rw_threads[alloc_pool].data = data
        self.rw_threads[alloc_pool].operation = operation
        self.thread_buffer[self.gen_thread_id] = None
        self.rw_threads[alloc_pool].buffer = self.thread_buffer[self.gen_thread_id]
        self.rw_threads[alloc_pool].start()
        return self.gen_thread_id
        
    def get_thread_buffer(self, thread_id):
        try:
            return self.thread_buffer[thread_id]
        except Exception as e:
            return "No thread"

    def remove_thread_buffer(self, thread_id):
        del self.thread_buffer[thread_id]

    def end_pool(self):
        self.end_flag = False

    def run(self):
        while self.end_flag:
            pass

class rw_operation():

    def __init__(self, filename):
        self.filename = filename


    #writing to file by appending "shad"
    def op_1(self, data):
        return data + "shad"



class rw_thread(threading.Thread):

    def __init__(self, thread_number, evt, filename, mutex=False):
        self.thread_number = thread_number
        self.mutex = mutex
        self.evt = evt
        self.buffer = None
        self.filename = filename
        super(rw_thread, self).__init__()

    def multi_ops(self, operation):
        if not self.evt.is_set():
            self.evt.wait()
        self.evt.clear()
        with open(self.filename, 'r+w') as f:
            data = f.read()
            if str(type(operation)) == "function":
                x = operation(data)
                if x is not None:
                    f.write(x)
                else:
                    raise RuntimeError("Mode: multi takes function of a argument and return string as argument")
            else:
                raise RuntimeError("Mode: multi takes function of a argument as argument")


    def read(self):
        if not self.evt.is_set():
            self.evt.wait()
        with open(self.filename, 'r') as f:
            data = f.read()
        return data

    def write(self, data):
        if not self.evt.is_set():
            self.evt.wait()
        print "hello"
        self.evt.clear()
        with open(self.filename, 'w') as f:
            f.write(data)

    def run(self):
        self.mutex = True
        logging.info("Thread id: {}, data: {}, operation: {}".format(self.thread_number, self.data, self.mode))
        if self.mode == "read":
            try:
                self.buffer = {"Read: success": self.read()}
            except Exception as e:
                self.buffer = {"Read: failure": e}
        elif self.mode == "write":
            try:
                self.write(self.data)
                self.buffer = {"Write: success": 0}
            except Exception as e:
                self.buffer = {"Write: failure": e}
            finally:
                self.evt.set()
        elif self.mode == "multi":
            try:
                self.multi_ops(self.operation)
                self.buffer = {"Operation: success": 0}
            except Exception as e:
                self.buffer = {"Operation: failure": e}
            finally:
                self.evt.set()
        else:
            self.buffer = {"No operation": -1}
        logging.info("Ending thread number: {}, iter: {}, buffer {}".format(self.thread_number, self.data, self.buffer))
        self.mutex = False

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    pool_1 = rw_pool(20, "thread_test.txt")

    mode = ["read", "write", "multi"]

    thread_list = []

    for i in range(200):
        thread_id = pool_1.action( mode[i%3], "thia ia operation {}, iteration {}".format(mode[i%3], i) )
        thread_list.append(thread_id)
    
    
    while len(thread_list) <= 0:
        for li in thread_list:
            if pool_1.get_thread_buffer(li) is not str and pool_1.get_thread_buffer(li) != "No thread":
                logger.info(pool_1.get_thread_buffer(li))
                pool_1.remove_thread_buffer(li)
                thread_list.remove(li)
            else:
                logger.info("Buffer id: {} is not ready".format(li))
        time.sleep(2)

    
