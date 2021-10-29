#!/usr/bin/env python3
import random as rand
list_size = int(input("How large of a list should we create? "))
rand_seed = rand.randint(1,10)
with open (f'words-{rand_seed}.txt', 'a+') as file:
    
    for i in range(0, list_size):
        rand_no = rand.randint(10**11, 10**12)
        file.write(str(rand_no)+'\n')
