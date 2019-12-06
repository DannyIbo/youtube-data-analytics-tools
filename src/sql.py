import time
import random

def set_temp_id():
    '''Create a random string by using current unix time and random integer of 4 digits.'''
    time_id = str(int(time.time()))
    rand_id = str(random.randint(1000,9999))
    temp_id = time_id + "_" + rand_id
    
    return temp_id
