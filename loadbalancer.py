#!/usr/bin/env python3
import random as rand
import enumeration.ecrpubenum as ecrpubenum
import enumeration.snsenum as snsenum
import enumeration.ecrprivenum as ecrprivenum
import os
import threading
import queue
import datetime
import settings
from os.path import exists

# Function to get a wordlist and ask how many threads, then split the wordlist into sub-wordlists of the appropriate size to generate the number of threads desired (approx) when passed to the threader function
def getter(wordlist):
    print('')
    threads = input('How many threads do you want to run? ')
    with open(wordlist) as file:
        my_list = [x.rstrip() for x in file]
    list_size = int(len(my_list)/int(threads))
    if list_size >= 1:
        list_size
    else:
        list_size = 1
    low_speed = (int(len(my_list))/700)/60
    high_speed = (int(len(my_list))/1100)/60
    print('')
    print("Estimated Scan Length: "+str(high_speed)+" minutes to "+str(low_speed)+" minutes")
    chunks = [my_list [x:x+list_size] for x in range (0, len(my_list), list_size)]
    new_list = []
    for list in chunks:
        new_list.append(list)
    print('')
    print('Scanning Started with Quiet Riot')
    return new_list

# Function to server as a crude load balancer for the service we know can withstand a significant load.
def balancedchecker(*wordlist):
    #create empty list of valid principals identified by scanning
    valid_list = []
    # iterate over wordlist and allocate wordlist to enumeration service based on a random seed selected at time of function call
    rand_seed = rand.randint(0, 1000)
    # TODO: Turn print statement into variable passed to the relevant princ_checker function for inclusion - eg: print(settings.scan_objects)
    for i in range(0, len(wordlist)):
        if 0 <= rand_seed <= 499: #ECR-Public seem to have best capacity or comparable to best - can handle nearly 1100 request/sec @ 278 threads
            if ecrpubenum.ecr_princ_checker(wordlist[i]) == 'Pass':
                valid_list.append(wordlist[i])
            else:
                pass
        elif 500 <= rand_seed <= 899:
            if snsenum.sns_princ_checker(wordlist[i]) == 'Pass': #SNS can handle maybe 220 threads? Test this # next
                valid_list.append(wordlist[i])
            else:
                pass
        elif 900 <= rand_seed <= 1000:
            if ecrprivenum.ecr_princ_checker(wordlist[i]) == 'Pass': #ECR-Private is able to handle maybe 80 threads
                valid_list.append(wordlist[i])
            else:
                pass
        else:
            print('No Action Taken')
    if valid_list == 0:
        pass
    else:
        q.put(valid_list)

# Function to create a bunch of threads so we can go faster.
threads = []
new_list = []
q = queue.Queue()
def threader(words):
    print('')
    print('Identified Valid Principals:')
    ct1 = datetime.datetime.now()
    ts1 = ct1.timestamp()
    for list in words:
        x = threading.Thread(target=balancedchecker, args=(list))
        x.start()
        threads.append(x)
        #x.join()
    for i in threads:
        new_list.append(q.get(i))
    flat_list = [item for sublist in new_list for item in sublist]
    with open ('results/Valid_Account_IDs.txt', 'a+') as file:
        for i in flat_list:
            file.write(str(i)+'\n')
    ct2 = datetime.datetime.now()
    ts2 = ct2.timestamp()
    print('')
    print('Scan Summary: ')
    print('# of Identified Valid Principals: '+str(len(flat_list)))
    print('# of Minutes Elapsed: '+str(int(ts2-ts1)/60))
    print("# of Threads Utilized: "+str(len(threads)))
    if exists('words.txt'):
        os.remove('words.txt')
    else:
        pass