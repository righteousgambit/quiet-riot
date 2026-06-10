#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import glob
import logging
import os
import random as rand
import time

from . import ecrprivenum, ecrpubenum, snsenum

logger = logging.getLogger(__name__)

timestamp = time.strftime("%Y%m%d-%H%M%S")


# Function to get a wordlist and ask how many threads, then split the wordlist into sub-wordlists of the appropriate size to generate the number of threads desired (approx) when passed to the threader function
def getter(thread, wordlist):
    # print('')
    # print('Approximately how many threads do you think you want to run?')
    # print('')
    # print('Hint: 2020 M1 Macbook Air w/ 16 GB RAM optimizes @ around 700 threads from limited testing.')
    # print('')
    threads = thread
    with open(wordlist) as file:
        my_list = [x.rstrip() for x in file]
    list_size = int(len(my_list) / int(threads))
    if list_size < 1:
        list_size = 1
    # Calculate estimated completion time based on 700 attempts/sec the 1100 attempts/sec
    low_speed = (int(len(my_list)) / 700) / 60
    high_speed = (int(len(my_list)) / 1100) / 60
    logger.info(f"Estimated Scan Duration: {int(high_speed)} minutes to {int(low_speed)} minutes")
    # Based on the number of desired threads and the overall # of words in the wordlist provided, chunk the wordlist into smaller wordlists and then make a list of lists that can be passed in threader to services
    chunks = [my_list[x : x + list_size] for x in range(0, len(my_list), list_size)]
    new_list = []
    for list in chunks:
        new_list.append(list)
    logger.info("Scanning Started with Quiet Riot")
    return new_list


# Function to serve as a crude load balancer for the services we know can withstand a significant load.
def balancedchecker(wordlist_chunk, session):
    """
    Check a chunk of principals against AWS services using load balancing.

    Args:
        wordlist_chunk: List of principals to check
        session: Boto3 session object

    Returns:
        List of valid principals found
    """
    # Create empty list of valid principals identified by scanning
    valid_list = []

    # Iterate over wordlist and allocate to enumeration service based on random distribution
    # Distribution: 75% ECR-Public, 17% SNS, 8% ECR-Private
    for principal in wordlist_chunk:
        # Generate random seed per item for better distribution
        rand_seed = rand.randint(0, 1000)
        try:
            if 0 <= rand_seed <= 749:
                # 75% - ECR Public
                if ecrpubenum.ecr_princ_checker(principal, session) == "Pass":
                    valid_list.append(principal)
            elif 750 <= rand_seed <= 919:
                # 17% - SNS
                if snsenum.sns_princ_checker(principal, session) == "Pass":
                    valid_list.append(principal)
            elif 920 <= rand_seed <= 1000:
                # 8% - ECR Private
                if ecrprivenum.ecr_princ_checker(principal, session) == "Pass":
                    valid_list.append(principal)
        except Exception as e:
            logger.warning(f"Error checking principal {principal}: {e}")
            continue

    return valid_list


# Function to create threads and execute parallel scanning
def threader(words, session):
    """
    Execute parallel scanning using ThreadPoolExecutor for proper thread management.

    Args:
        words: List of wordlist chunks (list of lists)
        session: Boto3 session object

    Returns:
        Path to results file
    """
    logger.info("Identified Valid Principals:")
    ct1 = datetime.datetime.now()
    ts1 = ct1.timestamp()

    # Flatten for total count calculation
    length_check = [item for sublist in words for item in sublist]
    total_items = len(length_check)

    # Collect all valid results
    all_valid_results = []
    threads_used = len(words)

    # Use ThreadPoolExecutor for proper thread management and cleanup
    with ThreadPoolExecutor(max_workers=threads_used) as executor:
        # Submit all tasks
        future_to_chunk = {executor.submit(balancedchecker, chunk, session): chunk for chunk in words}

        # Collect results as they complete
        for future in as_completed(future_to_chunk):
            chunk = future_to_chunk[future]
            try:
                valid_results = future.result()
                if valid_results:
                    all_valid_results.extend(valid_results)
                    # Log valid principals as they're found
                    for principal in valid_results:
                        logger.info(principal)
            except Exception as e:
                logger.error(f"Error processing chunk: {e}")
                continue

    # Write results to file
    results_file = f"valid_scan_results-{timestamp}.txt"
    with open(results_file, "a+") as file:
        for principal in all_valid_results:
            file.write(str(principal) + "\n")

    ct2 = datetime.datetime.now()
    ts2 = ct2.timestamp()
    elapsed_minutes = (ts2 - ts1) / 60

    # Provide basic stats on scan performance
    logger.info("Scan Summary: ")
    logger.info(f"# of Identified Valid Principals: {len(all_valid_results)}")
    logger.info(f"# of Scanned Principals: {total_items}")
    if total_items > 0:
        percent = (len(all_valid_results) / total_items) * 100
        logger.info(f"% Valid Principals: {percent:.2f}%")
    logger.info(f"# of Minutes Elapsed: {elapsed_minutes:.2f}")
    logger.info(f"# of Threads Utilized: {threads_used}")

    # Clean up temporary wordlist files if id_generator was used
    fileList = glob.glob("words-**")
    for filePath in fileList:
        try:
            filePath_two = os.path.join(os.getcwd(), filePath)
            os.remove(filePath_two)
        except Exception as f:
            logger.warning(f"Error while deleting file {filePath_two}: {f}")

    return results_file
