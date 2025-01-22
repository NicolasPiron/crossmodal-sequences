from time import sleep
from time import time

t1 = time()
for i in range(10, 0, -1):
    # update opacity function
    sleep(5/10)
t2 = time()
print(t2 - t1)