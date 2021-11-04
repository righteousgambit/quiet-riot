from quiet_riot.infra.quiet_infra import QuietInfra
import random as rand
import queue
import datetime
import threading
import glob
import os


class ThreadManager:
    def __init__(self, quiet_infra: QuietInfra, wordlist: list, thread_count: int = 700):
        self.wordlist = wordlist
        self.thread_count = thread_count
        self.quiet_infra = quiet_infra
        self.queue = queue.Queue()

    def get_chunked_wordlist(self):
        """Function to get a wordlist and ask how many threads, then split the wordlist into sub-wordlists of the
        appropriate size to generate the number of threads desired (approx) when passed to the threader function"""
        print('')
        print('Approximately how many threads do you think you want to run?')
        print('')
        print('Hint: 2020 M1 Macbook Air w/ 16 GB RAM optimizes @ around 700 threads from limited testing.')
        print('')

        list_size = int(len(self.wordlist) / int(self.thread_count))
        if list_size >= 1:
            # list_size
            pass
        else:
            list_size = 1
        # Calculate estimated completion time based on 700 attempts/sec the 1100 attempts/sec
        low_speed = (int(len(self.wordlist)) / 700) / 60
        high_speed = (int(len(self.wordlist)) / 1100) / 60
        print('')
        print("Estimated Scan Duration: " + str(int(high_speed)) + " minutes to " + str(int(low_speed)) + " minutes")
        # Based on the number of desired threads and the overall # of words in the wordlist provided, chunk the wordlist into smaller wordlists and then make a list of lists that can be passed in threader to services
        chunks = [self.wordlist[x:x + list_size] for x in range(0, len(self.wordlist), list_size)]
        new_list = []
        for list in chunks:
            new_list.append(list)
        print('')
        print('Scanning Started with Quiet Riot')
        return new_list

    def checker(self, *wordlist):
        """Function to server as a crude load balancer for the services we know can withstand a significant load."""
        # create empty list of valid principals identified by scanning
        valid_list = []
        # iterate over wordlist and allocate wordlist to enumeration service based on a random seed selected at time of function call
        rand_seed = rand.randint(0, 1000)
        for i in range(0, len(wordlist)):
            if 0 <= rand_seed <= 549:
                if self.quiet_infra.ecr_public_repo.principal_check(wordlist[i]) == 'Pass':
                    valid_list.append(wordlist[i])
                else:
                    pass
            elif 550 <= rand_seed <= 919:
                if self.quiet_infra.sns_topic.principal_check(wordlist[i]) == 'Pass':
                    valid_list.append(wordlist[i])
                else:
                    pass
            elif 920 <= rand_seed <= 1000:
                if self.quiet_infra.ecr_private_repo.principal_check(wordlist[i]) == 'Pass':
                    valid_list.append(wordlist[i])
                else:
                    pass
            else:
                print('Your rand_seed generator aint good at math')
        if valid_list == 0:
            pass
        else:
            self.queue.put(valid_list)

    def scan_with_threads(self, print_statistics: bool = True):
        """threader: Function to create a bunch of threads so we can go faster."""
        threads = []
        new_list = []

        print('')
        print('Identified Valid Principals:')
        ct1 = datetime.datetime.now()
        ts1 = ct1.timestamp()
        chunked_wordlist = self.get_chunked_wordlist()
        # For each list in the list of lists - trigger the "load balanced" principal checker
        for sub_wordlist in chunked_wordlist:
            x = threading.Thread(target=self.checker, args=sub_wordlist)
            x.start()
            threads.append(x)
            # x.join()
        # Take the returns for each thread (a list of valid results) and make a list from them.
        for i in threads:
            new_list.append(self.queue.get(i))
        # Flatten the new list
        flat_list = [item for sublist in new_list for item in sublist]
        # # Write the results to valid_scan_results.txt in the results/ folder
        # with open('results/valid_scan_results.txt', 'a+') as file:
        #     for i in flat_list:
        #         file.write(str(i) + '\n')
        ct2 = datetime.datetime.now()
        ts2 = ct2.timestamp()
        if print_statistics:
            # Provide basic stats on scan performance.
            print('')
            print('Scan Summary: ')
            print('# of Identified Valid Principals: ' + str(len(flat_list)))
            print('# of Minutes Elapsed: ' + str(int(ts2 - ts1) / 60))
            print("# of Threads Utilized: " + str(len(threads)))
            print('')

        print('Scan results can be found in the results sub-directory, if any valid_scan_results were identified.')
        # If the id_generator was used to create words.txt, you'll want to clean that up, so we do.
        fileList = glob.glob("words-*")
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file: ", filePath)
        return flat_list
