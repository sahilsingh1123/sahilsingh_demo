"""
We need create producer - consumer
in core python

# shared source between producer and consumer

"""
import queue
import random
import threading
import time

buffer = queue.Queue(maxsize=10)

def producer():
    i = 1
    while True:
        time.sleep(random.uniform(1, 3))
        item = f"item-{i}"
        buffer.put(item)
        print(f"Produer produced - {item}")
        i += 1

def consumer():
    while True:
        item = buffer.get()
        print(f"Consumed - {item}")
        time.sleep(random.uniform(4,8))
        buffer.task_done()




producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

while True:
    time.sleep(10)

