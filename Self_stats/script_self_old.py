import keyboard
from time import *
# import time
import pandas as pd
from numpy import floor
# time.asctime()

# help(time)
# help(keyboard)
# data = {'Time' : }
# df = pd.DataFrame(data, columns = ['Name', 'Age'])


times_acs = []
times = []
sleep(1)
key = None
while key != 'space':
    key = keyboard.read_key()

    t = int(floor(time()))
    t_asc = asctime()
    times.append(t)
    times_acs.append(t_asc)
    print(t)
    sleep(.1)
