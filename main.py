#!/usr/bin/env python3
import boto3
import time
import sys
import uuid
import time
import os
from os import environ
import glob
import loadbalancer
import enumeration.ecrprivenum
import enumeration.ecrpubenum
import enumeration.snsenum
import settings

from botocore.config import Config

config = Config(
    retries = dict(
        max_attempts = 7
    )
)

#Define ANSI escape sequence colors
environ["PYTHONIOENCODING"] = "UTF-8"
orange = "\033[3;33m"
green = "\033[0;32m"
red = "\033[9=0;31m"
nocolor = "\033[0m"

#Create timestamp in preferred format for wordlist files
timestamp = time.strftime("%Y%m%d-%H%M%S")

#Deploy infrastructure for scanning
print(green+f"""
________        .__        __    __________.__        __   
\_____  \  __ __|__| _____/  |_  \______   \__| _____/  |_ 
 /  / \  \|  |  \  |/ __ \   __\  |       _/  |/  _ \   __/
/   \_/.  \  |  /  \  ___/|  |    |    |   \  (  <_> )  |  
\_____\ \_/____/|__|\___  >__|    |____|_  /__|\____/|__|  
       \__>             \/               \/                
"""+nocolor)


#Create clients required for Quiet Riot Application Infrastructure
#s3 = boto3.client('s3')
#client = boto3.client('lambda')

# Set s3 resource client - allows operations against s3 buckets (data plane) rather than s3 service (control plane)
#s3resource = boto3.resource(service_name = 's3')
sts = boto3.client('sts')
#Create clients required for Quiet Riot Enumeration Infrastructure
sns = boto3.client('sns', config = config)
ecrprivate = boto3.client('ecr', config = config)
ecrpublic = boto3.client('ecr-public', config = config)

#global_bucket = 's3://quiet-riot-global-bucket/'

#Create s3 bucket to use for Lambda trigger
#bucket_name = 'quiet-riot-global-bucket' #f'quiet-riot-infra-bucket-{uuid.uuid4().hex}'
# s3.create_bucket(ACL='bucket-owner-full-control',
#     Bucket=bucket_name,
#     )
# Command to upload results file 
# s3resource.meta.client.upload_file(Filename = 'words.txt', Bucket = bucket_name, Key = 'results/valid-principals.txt')





#Requests user to provide required info to kick off scan
def words_type():
    wordlist_type=input("\033[0;31m"+'Wordlist is intended to be accounts, roles, users, or root account? '+"\033[0m").lower()
    print('')
    while True:
        if wordlist_type == 'accounts':
            return 'accounts', 'none'
        elif wordlist_type == 'root account':
            return 'root-account', 'none'
        elif wordlist_type == 'roles':
            account_no=input('Please provide an Account ID to scan against: ')
            print('')
            return 'roles', account_no
        elif wordlist_type == 'users':
            account_no=input('Please provide an Account ID to scan against: ')
            print('')
            return 'users', account_no
        elif wordlist_type == 'groups':
            account_no=input('Please provide an Account ID to scan against: ')
            print('')
            return 'groups', account_no
        else:
            print('You did not enter a valid wordlist type.')
            print('')
            wordlist_type=input("\033[0;31m"+'Wordlist is intended to be accounts, roles, users, or root account? '+"\033[0m").lower()

#Creates final wordlist based on type of scanning to be performed.
def words():
    wordlist_type, account_no = words_type()
    wordlist = 'wordlist-'+wordlist_type+'-'+timestamp+'.txt'
    new_list = []
    while True:
        try:
            wordlist_file=input('Provide path to wordlist file: ')
            print('')
            with open(wordlist_file) as file:
                my_list = [x.rstrip() for x in file]   
                if wordlist_type == 'roles':
                    for item in my_list:
                        new_list.append('arn:aws:iam::'+account_no+':role/'+item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as roles for triggering via enumeration.loadbalancer.threader(getter())
                    loadbalancer.threader(loadbalancer.getter(wordlist=wordlist))
                    break
                elif wordlist_type == 'users':
                    for item in my_list:
                        new_list.append('arn:aws:iam::'+account_no+':user/'+item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as users for triggering via enumeration.loadbalancer.threader(getter())
                    loadbalancer.threader(loadbalancer.getter(wordlist=wordlist))
                    break
                elif wordlist_type == 'accounts' or 'root account':
                    for item in my_list:
                        new_list.append(item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as account IDs or root account e-mails for triggering via enumeration.loadbalancer.threader(getter())
                    loadbalancer.threader(loadbalancer.getter(wordlist=wordlist))
                    break
                else: 
                    print('Scan type provided is not valid.')
                    wordlist_type=input("\033[0;31m"+'Wordlist is intended to be accounts, roles, users, groups, or root account? '+"\033[0m").lower()
        except OSError:
            print('')
            print('Provided filename does not appear to exist.')
            print('')
            continue


#############################################################################
##                                                                         ##
##           Deployment of Enumeration Infra based on user preference      ##
##                                                                         ##
#############################################################################

#Create ECR Public Repository - Resource that has IAM policy attachment
ecr_public_repo = f'quiet-riot-public-repo-{uuid.uuid4().hex}'
ecrpublic.create_repository(
    repositoryName=ecr_public_repo
)
#Create ECR Private Repository - Resource that has IAM policy attachment
ecr_private_repo = f'quiet-riot-private-repo-{uuid.uuid4().hex}'
ecrprivate.create_repository(
    repositoryName=ecr_private_repo
)
#Create SNS Topic - Resource that has IAM policy attachment
sns_topic = f'quiet-riot-sns-topic-{uuid.uuid4().hex}'
sns.create_topic(
    Name=sns_topic
)

# Create list from created resource names
settings.init()
settings.scan_objects.append(ecr_public_repo) 
settings.scan_objects.append(ecr_private_repo) 
settings.scan_objects.append("arn:aws:sns:us-east-1:"+settings.account_no+":"+sns_topic)

words() # TODO: words(scan_objects) - where words takes scan_objects and passes it as a second parameter to getter() - getter() then takes 

#Request whether user is finished with infrastructure

while True:
    print('')
    time.sleep(1)
    prompt1=input('Finished Scanning? Answer "yes" to delete your infrastructure: ').lower()
    time.sleep(1)
    #If user is finished with infrastructure, delete the created infrastructure
    if prompt1 == 'yes':
        #Delete ECR Public Repository - Resource that has IAM policy attachment
        ecrpublic.delete_repository(
            repositoryName=ecr_public_repo
        )
        #Delete ECR Private Repository - Resource that has IAM policy attachment
        ecrprivate.delete_repository(
            repositoryName=ecr_private_repo
        )
        #Delete SNS Topic - Resource that has IAM policy attachment
        sns_topics = sns.list_topics()
        sns_target_arn = sns_topics['Topics'][0]['TopicArn']
        sns.delete_topic(
            TopicArn= f'{sns_target_arn}'
        )
        print('')
        #Ask user if they want valid principals file downloaded
        print('')
        # TODO: Create control flow logic to ask user if willing to upload valid principals to global quiet-riot bucket maintained by Righteous Gambit Research
        fileList=glob.glob("wordlist-*")
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file: ", filePath)
        sys.exit()
    elif prompt1 == 'no':
        print('')
        print("\033[0;32m"+f'If you have uploaded a wordlist, you can review your validated principals @ valid_principals.txt in your local directory.'+"\033[0m")
        print('')
        keep_going=input('Configure another wordlist? ').lower()
        print('')
        if keep_going == 'yes':
            words()
        elif keep_going == 'no':
            pass
        else:
            print('Provided response is not valid. Response must be "yes" or "no".')
            print('')
            keep_going=input('Configure another wordlist? ').lower()
    else:
        print('')
        print('Provided response is not valid. Response must be "yes" or "no".')