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
    print('Approximately how many threads do you think you want to run?')
    print('')
    print('Hint: 2020 M1 Macbook Air w/ 16 GB RAM optimizes @ around 700 threads from limited testing.')
    print('')
    threads = input('# of threads: ')
    with open(wordlist) as file:
        my_list = [x.rstrip() for x in file]
    list_size = int(len(my_list)/int(threads))
    if list_size >= 1:
        list_size
    else:
        list_size = 1
    # Calculate estimated completion time based on 700 attempts/sec the 1100 attempts/sec
    low_speed = (int(len(my_list))/700)/60
    high_speed = (int(len(my_list))/1100)/60
    print('')
    print("Estimated Scan Duration: "+str(int(high_speed))+" minutes to "+str(int(low_speed))+" minutes")
    # Based on the number of desired threads and the overall # of words in the wordlist provided, chunk the wordlist into smaller wordlists and then make a list of lists that can be passed in threader to services
    chunks = [my_list [x:x+list_size] for x in range (0, len(my_list), list_size)]
    new_list = []
    for list in chunks:
        new_list.append(list)
    print('')
    print('Scanning Started with Quiet Riot')
    return new_list

# Function to server as a crude load balancer for the services we know can withstand a significant load.
def balancedchecker(*wordlist):
    #create empty list of valid principals identified by scanning
    valid_list = []
    # iterate over wordlist and allocate wordlist to enumeration service based on a random seed selected at time of function call
    rand_seed = rand.randint(0, 1000)
    for i in range(0, len(wordlist)):
        if 0 <= rand_seed <= 549:
            if ecrpubenum.ecr_princ_checker(wordlist[i]) == 'Pass':
                valid_list.append(wordlist[i])
            else:
                pass
        elif 550 <= rand_seed <= 899:
            if snsenum.sns_princ_checker(wordlist[i]) == 'Pass':
                valid_list.append(wordlist[i])
            else:
                pass
        elif 920 <= rand_seed <= 1000:
            if ecrprivenum.ecr_princ_checker(wordlist[i]) == 'Pass':
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
    # For each list in the list of lists - trigger the "load balanced" principal checker
    for list in words:
        x = threading.Thread(target=balancedchecker, args=(list))
        x.start()
        threads.append(x)
        #x.join()
    # Take the returns for each thread (a list of valid results) and make a list from them.
    for i in threads:
        new_list.append(q.get(i))
    # Flatten the new list
    flat_list = [item for sublist in new_list for item in sublist]
    # Write the results to valid_scan_results.txt in the results/ folder
    with open ('wordlists/provided_account_ids.txt', 'a+') as file:
        for i in flat_list:
            file.write(str(i)+'\n')
    ct2 = datetime.datetime.now()
    ts2 = ct2.timestamp()
    # Provide basic stats on scan performance.
    print('')
    print('Scan Summary: ')
    print('# of Identified Valid Principals: '+str(len(flat_list)))
    print('# of Minutes Elapsed: '+str(int(ts2-ts1)/60))
    print("# of Threads Utilized: "+str(len(threads)))
    print('')
    print('Scan results can be found in the results sub-directory, if any valid_scan_results were identified.')
    # If the id_generator was used to create words.txt, you'll want to clean that up, so we do.
    if exists('words.txt'):
        os.remove('words.txt')
    else:
        pass