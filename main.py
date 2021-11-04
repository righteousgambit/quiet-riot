#!/usr/bin/env python3
import boto3
import time
import sys
import uuid
import time
import os
from os import environ
import glob
import enumeration.loadbalancer as loadbalancer
import enumeration.rand_id_generator as rand_id_generator
import enumeration.s3aclenum as s3aclenum
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



sts = boto3.client('sts')
#Create clients required for Quiet Riot Enumeration Infrastructure
s3 = boto3.client('s3', config = config)
sns = boto3.client('sns', config = config)
ecrprivate = boto3.client('ecr', config = config)
ecrpublic = boto3.client('ecr-public', config = config)

#global_bucket = 's3://quiet-riot-global-bucket/'

#Requests user to provide required info to kick off scan
def words_type():
    print(("\033[0;31m"+'What type of scan do you want to attempt? '+"\033[0m"))
    print('1. accounts')
    print('2. root account')
    print('3. account footprint')
    print('4. roles')
    print('5. users')
    print()
    wordlist_type=input('Scan Type: ').lower()
    print('')
    while True:
        if wordlist_type == '1':
            return 'accounts', 'none'
        elif wordlist_type == '2':
            return 'root account', 'none'
        elif wordlist_type == 'roles':
            account_no=input('Provide an Account ID to scan against: ')
            print('')
            return 'roles', account_no
        elif wordlist_type == '3':
            account_no=input('Provide an Account ID to scan against: ')
            print('')
            return 'footprint', account_no
        elif wordlist_type == '4':
            account_no=input('Provide an Account ID to scan against: ')
            print('')
            return 'roles', account_no
        elif wordlist_type == '5':
            account_no=input('Provide an Account ID to scan against: ')
            print('')
            return 'users', account_no
        else:
            print('You did not enter a valid wordlist type.')
            print('')
            wordlist_type=input("\033[0;31m"+'Enter a number between 1-5 '+"\033[0m").lower()

#Creates final wordlist based on type of scanning to be performed.
def words():
    wordlist_type, account_no = words_type()
    wordlist = 'wordlist-'+wordlist_type+'-'+timestamp+'.txt'
    new_list = []
    while True:
        try:
            if wordlist_type == 'accounts':
                response = rand_id_generator.rand_id_generator()
                wordlist_file = response
            elif wordlist_type == 'footprint':
                wordlist_file = 'wordlists/service-linked-roles.txt'
            else:
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
                elif wordlist_type == 'footprint':
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
                # TODO: Separate root accounts and setup s3 ACL check for root e-mail. Determine if root e-mail is only enumerable using s3 ACL
                elif wordlist_type == 'accounts':
                    for item in my_list:
                        new_list.append(item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as account IDs or root account e-mails for triggering via enumeration.loadbalancer.threader(getter())
                    loadbalancer.threader(loadbalancer.getter(wordlist=wordlist))
                    break
                elif wordlist_type == 'root account':
                    valid_emails = []
                    print('Indentified Root Account E-mail Addresses:')
                    for i in my_list:
                        if s3aclenum.s3_acl_princ_checker(i) == 'Pass':
                            print(i)
                            valid_emails.append(i)
                        else:
                            pass
                    with open ('results/valid_scan_results.txt', 'a+') as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)
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

#Create s3 bucket to scan against
s3_bucket = f'quiet-riot-bucket-{uuid.uuid4().hex}'
s3.create_bucket(
    Bucket=s3_bucket
)

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

canonical_id = s3.list_buckets()['Owner']['ID']
# Create list from created resource names
settings.init()
settings.scan_objects.append(ecr_public_repo) 
settings.scan_objects.append(ecr_private_repo) 
settings.scan_objects.append("arn:aws:sns:us-east-1:"+settings.account_no+":"+sns_topic)
settings.scan_objects.append(canonical_id)

print(canonical_id)
# Call initial workflow that takes a user wordlist and starts a scan.
words()

#Request whether user is finished with infrastructure

while True:
    print('')
    time.sleep(1)
    prompt1= 'yes'# TODO: figure out why it can't take "no" - the threads never finish a second time through...think I need to clear the threads... #input('Finished Scanning? Answer "yes" to delete your infrastructure: ').lower()
    time.sleep(1)
    #If user is finished with infrastructure, delete the created infrastructure
    if prompt1 == 'yes':
        buckets = s3.list_buckets()
        for i in range(0, len(buckets['Buckets'])):
            if len(buckets['Buckets']) != 0:
                if 'quiet-riot-bucket' in buckets['Buckets'][i]['Name']:
                    print("Deleting Quiet Riot Infrastructure: " +buckets['Buckets'][i]['Name'])
                    s3.delete_bucket(Bucket= buckets['Buckets'][i]['Name'])
                else:
                    pass
        #Delete ECR Public Repository - Resource that has IAM policy attachment
        public_repos = ecrpublic.describe_repositories()
        for i in range(0, len(public_repos['repositories'])):
            if len(public_repos['repositories']) != 0:
                if 'quiet-riot-public-repo' in public_repos['repositories'][i]['repositoryName']:
                    print("Deleting Quiet Riot Infrastructure: " +public_repos['repositories'][i]['repositoryName'])
                    ecrpublic.delete_repository(repositoryName= public_repos['repositories'][i]['repositoryName'])
                else:
                    pass
        #Delete ECR Private Repository - Resource that has IAM policy attachment
        private_repos = ecrprivate.describe_repositories()        
        for i in range(0, len(private_repos['repositories'])):
            if len(private_repos['repositories']) != 0:
                if 'quiet-riot-private-repo' in private_repos['repositories'][i]['repositoryName']:
                    print("Deleting Quiet Riot Infrastructure: " +private_repos['repositories'][i]['repositoryName'])
                    ecrprivate.delete_repository(repositoryName= private_repos['repositories'][i]['repositoryName'])
                else:
                    pass
        #Delete SNS Topic - Resource that has IAM policy attachment
        sns_topics = sns.list_topics()
        for i in range(0, len(sns_topics['Topics'])):
            if len(sns_topics['Topics']) != 0:
                if 'quiet-riot-sns-topic' in sns_topics['Topics'][i]['TopicArn']:
                    print("Deleting Quiet Riot Infrastructure: " +sns_topics['Topics'][i]['TopicArn'])
                    sns.delete_topic(TopicArn= sns_topics['Topics'][i]['TopicArn'])
                else:
                    pass
            else:
                print("There are no topics to delete.")
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