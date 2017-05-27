from queue import Queue
import threading
import time
import random

l = ['a','b','c','d','e']
q = Queue()
for i in l:
    q.put(i)

def run(str):
   for i in range(5):
        time.sleep(random.randint(1,10))
        print("this is thread: "+str)


thread_list = []
for i in l:
    t = threading.Thread(target=run,args=(i,))
    t.daemon = True
    t.start();
    thread_list.append(t)

for t in thread_list:
    t.join()



