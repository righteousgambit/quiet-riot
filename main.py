#!/usr/bin/env python3
import json
import textwrap
import boto3
import time
import sys
import argparse
import uuid
import os
from os import environ
import glob
from .enumeration import loadbalancer as loadbalancer
from .enumeration import rand_id_generator as rand_id_generator
from .enumeration import s3aclenum as s3aclenum
from .enumeration import ecrprivenum
from .enumeration import ecrpubenum
from .enumeration import snsenum
from . import settings
from botocore.config import Config
from pathlib import Path

# Define ANSI escape sequence colors


# Requests user to provide required info to kick off scan
def words_type(wordlist_type):
    while True:

        if str(wordlist_type) == '1':
            return 'accounts', 'none'
        elif str(wordlist_type) == '2':
            return 'root account', 'none'
        elif str(wordlist_type) == 'roles':
            account_no = input('Provide an Account ID to scan against: ')
            print('')
            return 'roles', str(account_no)
        elif str(wordlist_type) == '3':
            account_no = input('Provide an Account ID to scan against: ')
            print('')
            return 'footprint', str(account_no)
        elif str(wordlist_type) == '4':
            account_no = input('Provide an Account ID to scan against: ')
            print('')
            return 'roles', str(account_no)
        elif str(wordlist_type) == '5':
            account_no = input('Provide an Account ID to scan against: ')
            print('')
            return 'users', str(account_no)
        else:
            print('You did not enter a valid Scan type.')
            print('')
            wordlist_type = input("\033[0;31m" + 'Enter a number between 1-5 ' + "\033[0m").lower()


# Creates final wordlist based on type of scanning to be performed.
def words(input_args, wordlist_type, session):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    wordlist_type, account_no = words_type(wordlist_type)
    # print(wordlist_type)
    wordlist_path = 'wordlist-' + wordlist_type + '-' + timestamp + '.txt'
    wordlist = os.path.join(os.getcwd(), wordlist_path)
    new_list = []
    while True:
        try:
            if wordlist_type == 'accounts':
                response = rand_id_generator.rand_id_generator()
                wordlist_file = response
            elif wordlist_type == 'footprint':
                wordlist_file = os.path.dirname(__file__) + '/wordlists/service-linked-roles.txt'
            elif wordlist_type == 'root account':
                fileList = glob.glob("final_**")
                for filePath in fileList:
                    try:
                        main_path = os.getcwd()
                        wordlist_file = os.path.join(os.getcwd(), filePath)
                    except Exception as f:
                        print(f)
                        print("Error while deleting file: ", wordlist_file)

            else:
                if str(input_args.wordlist) == '':
                    wordlist_file = input("Provide the path to wordlist file : ")
                else:
                    wordlist_file = input_args.wordlist

            print('')
            with open(wordlist_file) as file:
                my_list = [x.rstrip() for x in file]
                file.close()
                if wordlist_type == 'roles':
                    for item in my_list:
                        new_list.append('arn:aws:iam::' + account_no + ':role/' + item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as roles for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session)
                    # print(results_file)
                    return results_file
                    break
                elif wordlist_type == 'footprint':
                    for item in my_list:
                        new_list.append('arn:aws:iam::' + account_no + ':role/' + item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as roles for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session)
                    return results_file
                    break
                elif wordlist_type == 'users':
                    for item in my_list:
                        new_list.append('arn:aws:iam::' + account_no + ':user/' + item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as users for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session)
                    return results_file
                    break
                # TODO: Separate root accounts and setup s3 ACL check for root e-mail. Determine if root e-mail is only enumerable using s3 ACL
                elif wordlist_type == 'accounts':
                    for item in my_list:
                        new_list.append(item)
                    with open(wordlist, 'a+') as f:
                        for item in new_list:
                            f.write("%s\n" % item)

                    # Configure user-defined wordlist as account IDs or root account e-mails for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session)
                    return results_file
                    break
                elif wordlist_type == 'root account':
                    valid_emails = []
                    print('')
                    print("Chcecking Emails for root account........")
                    print('')
                    print("Wait for the scaning process to complete it may take some time...............")
                    print('')
                    print('Indentified Root Account E-mail Addresses:')
                    print("................")
                    for i in my_list:
                        if s3aclenum.s3_acl_princ_checker(i, session) == 'Pass':
                            print(str(i) + " is a root account")
                            print("")
                            print(i)
                            valid_emails.append(i)
                        else:
                            pass
                    print("")
                    print("-----------Scaning Completed----------")
                    results_file = f'valid_scan_results-{timestamp}.txt'
                    with open(results_file, 'a+') as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)

                    f.close()
                    return results_file
                    break
                else:
                    print('Scan type provided is not valid.')
                    wordlist_type = input(
                        "\033[0;31m" + 'Wordlist is intended to be accounts, roles, users, groups, or root account? ' + "\033[0m").lower()

        except OSError as e:
            print('')
            print('Provided filename does not appear to exist.')
            print('Provided filename does not appear to exist.')
            print(e)
            continue


# def scan_inst():

def main():
    environ["PYTHONIOENCODING"] = "UTF-8"
    orange = "\033[3;33m"
    green = "\033[0;32m"
    red = "\033[9=0;31m"
    nocolor = "\033[0m"

    # Create timestamp in preferred format for wordlist files
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--scan', '--s', required=True, type=int, default=1,
                        help=textwrap.dedent('''\
                        What type of scan do you want to attempt? Enter the type of scan for example
                             1. Account IDs
                             2. Root Account E-mail Addresses
                             3. Service Footprint
                             4. IAM Principals
                                4.1. IAM Roles
                                4.2. IAM Users

                             '''))

    parser.add_argument('--threads', '--t', type=int, default=100,
                        help=textwrap.dedent('''\
                        Approximately how many threads do you think you want to run?

                        '''))

    parser.add_argument('--wordlist', '--w', type=str, default="",
                        help=textwrap.dedent('''\
                        Path to the world list file which will be required for scan

                        '''))

    parser.add_argument('--profile', '--p', type=str, default="default",
                        help=textwrap.dedent('''Name of aws profile  

                        '''))

    input_args = parser.parse_args()

    print("Input arguments : " + str(input_args))

    # Deploy infrastructure for scanning
    print(f"""
    ________        .__        __    __________.__        __   
    \_____  \  __ __|__| _____/  |_  \______   \__| _____/  |_ 
     /  / \  \|  |  \  |/ __ \   __\  |       _/  |/  _ \   __/
    /   \_/.  \  |  /  \  ___/|  |    |    |   \  (  <_> )  |  
    \_____\ \_/____/|__|\___  >__|    |____|_  /__|\____/|__|  
           \__>             \/               \/                
    """)
    aws_profile_name = input_args.profile

    session = boto3.Session(profile_name=f'{aws_profile_name}')
    # print(session)
    s3 = session.client('s3')
    sts = session.client('sts')
    iam = session.client('iam')
    sns = session.client('sns')
    ecrprivate = session.client('ecr')
    ecrpublic = session.client('ecr-public')

    wordlist_type = str(input_args.scan)

    def email_creation():

        family_names = os.path.dirname(__file__) + '/wordlists/familynames-usa-top1000.txt'

        female_name = os.path.dirname(__file__) + '/wordlists/femalenames-usa-top1000.txt'

        male_name = os.path.dirname(__file__) + '/wordlists/malenames-usa-top1000.txt'

        def email_type(email_type_text):
            while True:

                if str(email_type_text) == '1':
                    return 'first_type'
                elif str(email_type_text) == '2':
                    return 'second_type'
                elif str(email_type_text) == '3':
                    return 'third_type'
                elif str(email_type_text) == '4':
                    return 'fourth_type'
                elif str(email_type_text) == '5':
                    return 'fifth_type'

                else:
                    print('You did not enter a valid input.')
                    print('')
                    email_type_text = input("Enter a number between 1-5 : ").lower()
                    print('')

        print(
            "Which e-mail format you want? Enter the number between (1-5)\n1. [first name]@traingrcacademy.onmicrosoft.com\n2. [first name][Last name]@traingrcacademy.onmicrosoft.com\n3. [first name].[last name]@traingrcacademy.onmicrosoft.com\n4. [last name]@traingrcacademy.onmicrosoft.com\n5. [first name]_[last name]@traingrcacademy.onmicrosoft.com")
        email_type_text = input("Enter a number between 1-5 : ").lower()

        email_option = email_type(email_type_text)

        with open(family_names) as file:
            family_names_list = [x.rstrip() for x in file]

        with open(female_name) as file:
            female_names_list = [x.rstrip() for x in file]

        with open(male_name) as file:
            male_names_list = [x.rstrip() for x in file]

        combined_female_name = []
        for fam_name in family_names_list:

            for fe_name in female_names_list:
                female_final_name = fe_name + " " + fam_name

                combined_female_name.append(female_final_name)

        female_file = 'combined_female_names.txt'
        with open(female_file, 'w') as female_file:
            for i in combined_female_name:
                female_file.write(str(i) + '\n')

        female_file.close()

        combined_male_name = []
        for fam_name in family_names_list:

            for m_name in male_names_list:
                male_final_name = m_name + " " + fam_name

                combined_male_name.append(male_final_name)

        male_file = 'combined_male_names.txt'
        with open(male_file, 'w') as male_file:
            for i in combined_male_name:
                male_file.write(str(i) + '\n')

        male_file.close()

        random_final_names = combined_female_name + combined_male_name

        final_file = 'names_quit_riot.txt'
        with open(final_file, 'w') as final_file:
            for i in random_final_names:
                final_file.write(str(i) + '\n')

        final_file.close()

        email_list = []
        print('')
        print("Generating e-mails based on the format.........")
        print('')

        for name in random_final_names:

            name = name.lower()
            if str(email_option) == 'first_type':
                email = name.split(" ")[0] + "@traingrcacademy.onmicrosoft.com"
                email_list.append(email)

            elif str(email_option) == 'second_type':

                email = name.replace(" ", "") + "@traingrcacademy.onmicrosoft.com"
                email_list.append(email)

            elif str(email_option) == 'third_type':

                email = name.replace(" ", ".") + "@traingrcacademy.onmicrosoft.com"
                email_list.append(email)

            elif str(email_option) == 'fourth_type':

                email = name.split(" ")[1] + "@traingrcacademy.onmicrosoft.com"
                email_list.append(email)

            elif str(email_option) == 'fifth_type':

                email = name.replace(" ", "_") + "@traingrcacademy.onmicrosoft.com"
                email_list.append(email)

        email_list_set = set(email_list)

        email_set_list = (list(email_list_set))

        final_email = 'final_emails.txt'
        with open(final_email, 'w') as final_file:
            for i in email_set_list:
                final_file.write(str(i) + '\n')
        print("Total Number of e-mails generated : " + str(len(email_set_list)))

    def sub_scan_type():
        print("")
        print("1. IAM Roles")
        print("")

        print("2. IAM Users")
        print("")

        sub_iam_type = input("Kindly select one of the above scan types:")
        while True:
            if sub_iam_type == "1":
                wordlist_type = "4"
                return wordlist_type

            elif sub_iam_type == "2":
                wordlist_type = "5"
                return wordlist_type

            else:
                print('You did not enter a valid wordlist type.')
                print('')
                sub_iam_type = str(input("Enter a number 1 or 2 : "))

        # print(str(wordlist_type))

    if str(wordlist_type) == "4":
        wordlist_type = sub_scan_type()

    if str(wordlist_type) == "2":
        email_creation()

    # Create s3 bucket to scan against for root account e-mail addresses.

    # global_bucket = 's3://quiet-riot-global-bucket/'

    # initialize
    #############################################################################
    ##                                                                         ##
    ##           Deployment of Enumeration Infra based on user preference      ##
    ##                                                                         ##
    #############################################################################

    # Create ECR Public Repository - Resource that has IAM policy attachment
    ecr_public_repo = f'quiet-riot-public-repo-{uuid.uuid4().hex}'
    ecrpublic.create_repository(
        repositoryName=ecr_public_repo
    )
    # Create ECR Private Repository - Resource that has IAM policy attachment
    ecr_private_repo = f'quiet-riot-private-repo-{uuid.uuid4().hex}'
    ecrprivate.create_repository(
        repositoryName=ecr_private_repo
    )
    # Create SNS Topic - Resource that has IAM policy attachment
    sns_topic = f'quiet-riot-sns-topic-{uuid.uuid4().hex}'
    sns.create_topic(
        Name=sns_topic
    )
    # Create s3 bucket to scan against for root account e-mail addresses.
    s3_bucket = f'quiet-riot-bucket-{uuid.uuid4().hex}'
    s3.create_bucket(
        Bucket=s3_bucket
    )

    canonical_id = s3.list_buckets()['Owner']['ID']
    # Generate list from created resource names
    settings.init(session)
    settings.scan_objects.append(ecr_public_repo)
    settings.scan_objects.append(ecr_private_repo)
    settings.scan_objects.append("arn:aws:sns:us-east-1:" + settings.account_no + ":" + sns_topic)
    settings.scan_objects.append(s3_bucket)
    settings.scan_objects.append(canonical_id)
    # print("Calling the words function-------")
    # Call initial workflow that takes a user wordlist and starts a scan.

    account_arn = sts.get_caller_identity()['Arn']

    results_file = words(input_args, wordlist_type, session)
    # print(results_file)
    default_bucket_name = "quiet-riot-" + settings.account_no

    buckets = s3.list_buckets()
    bucket_flag = 0

    for i in range(0, len(buckets['Buckets'])):
        if str(default_bucket_name) in buckets['Buckets'][i]['Name']:
            bucket_flag = 1
            print("S3 bucket is already there with this name: " + default_bucket_name)
            break
        else:
            bucket_flag = 0
            pass

    if bucket_flag == 0:
        print("Creating S3 bucket for uploading results: " + default_bucket_name)
        s3_bucket = f'{str(default_bucket_name)}'
        s3.create_bucket(
            Bucket=s3_bucket,
            ACL='private'
        )
        response_public = s3.put_public_access_block(
            Bucket=f'{str(default_bucket_name)}',
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            },
        )

        time.sleep(4)

    try:
        result_file_path = os.path.join(os.getcwd(), results_file)
        s3.put_object(
            Body=open(f'{result_file_path}', 'rb'),
            Bucket=f'{default_bucket_name}',
            Key=f'{results_file}'
        )
        bucket_obj_url = s3.generate_presigned_url('get_object',
                                                   Params={'Bucket': default_bucket_name,
                                                           'Key': results_file},
                                                   ExpiresIn=604800)
        print("")
        print("Download your scan results:")
        print("")
        print(bucket_obj_url)
    except Exception as result_exc:
        print(result_exc)
        print("There is some error in uploading file to S3 bucket")

    try:

        results_file1 = glob.glob("valid_scan_results-*")

        for filePath_results in results_file1:

            try:
                # print(filePath)
                results_file_path = os.path.join(os.getcwd(), filePath_results)
                # print(results_file_path)
                os.remove(results_file_path)

            except Exception as result_file_exc:

                print(result_file_exc)
                print("Error while deleting  file")


    except Exception as result_file_exc:
        print(result_file_exc)

    # Request whether user is finished with infrastructure

    while True:
        print('')
        time.sleep(1)
        prompt1 = 'yes'  # TODO: figure out why it can't take "no" - the threads never finish a second time through...think I need to clear the threads... #input('Finished Scanning? Answer "yes" to delete your infrastructure: ').lower()
        time.sleep(1)
        # If user is finished with infrastructure, delete the created infrastructure
        if prompt1 == 'yes':
            buckets = s3.list_buckets()
            # print(buckets)
            for i in range(0, len(buckets['Buckets'])):
                if len(buckets['Buckets']) != 0:
                    if 'quiet-riot-bucket' in buckets['Buckets'][i]['Name']:
                        # print("Deleting Quiet Riot Infrastructure: " + buckets['Buckets'][i]['Name'])
                        s3.delete_bucket(Bucket=buckets['Buckets'][i]['Name'])
                    else:
                        pass
            # Delete ECR Public Repository - Resource that has IAM policy attachment
            public_repos = ecrpublic.describe_repositories()
            for i in range(0, len(public_repos['repositories'])):
                if len(public_repos['repositories']) != 0:
                    if 'quiet-riot-public-repo' in public_repos['repositories'][i]['repositoryName']:
                        # print(
                        #     "Deleting Quiet Riot Infrastructure: " + public_repos['repositories'][i]['repositoryName'])
                        ecrpublic.delete_repository(repositoryName=public_repos['repositories'][i]['repositoryName'])
                    else:
                        pass
            # Delete ECR Private Repository - Resource that has IAM policy attachment
            private_repos = ecrprivate.describe_repositories()
            for i in range(0, len(private_repos['repositories'])):
                if len(private_repos['repositories']) != 0:
                    if 'quiet-riot-private-repo' in private_repos['repositories'][i]['repositoryName']:
                        # print(
                        #     "Deleting Quiet Riot Infrastructure: " + private_repos['repositories'][i]['repositoryName'])
                        ecrprivate.delete_repository(repositoryName=private_repos['repositories'][i]['repositoryName'])
                    else:
                        pass
            # Delete SNS Topic - Resource that has IAM policy attachment
            sns_topics = sns.list_topics()
            for i in range(0, len(sns_topics['Topics'])):
                if len(sns_topics['Topics']) != 0:
                    if 'quiet-riot-sns-topic' in sns_topics['Topics'][i]['TopicArn']:
                        # print("Deleting Quiet Riot Infrastructure: " + sns_topics['Topics'][i]['TopicArn'])
                        sns.delete_topic(TopicArn=sns_topics['Topics'][i]['TopicArn'])
                    else:
                        pass
                else:
                    print("There are no topics to delete.")
            print('')
            # Ask user if they want valid principals file downloaded
            print('')
            # TODO: Create control flow logic to ask user if willing to upload valid principals to global quiet-riot bucket maintained by Righteous Gambit Research
            try:
                fileList = glob.glob("wordlist-**")
                for filePath in fileList:
                    try:
                        # print(filePath)
                        wordlist_file_path = os.path.join(os.getcwd(), filePath)
                        # print(wordlist_file_path)
                        os.remove(wordlist_file_path)
                    except Exception as text_file:
                        print(text_file)
                        print("Error while deleting wordlist file: ", wordlist_file_path)

            except Exception as wordlist_file_exc:
                print(wordlist_file_exc)

            sys.exit()
        elif prompt1 == 'no':
            print('')
            print(
                "\033[0;32m" + f'If you have uploaded a wordlist, you can review your validated principals @ valid_principals.txt in your local directory.' + "\033[0m")
            print('')
            keep_going = input('Configure another wordlist? ').lower()
            print('')
            if keep_going == 'yes':
                words()
            elif keep_going == 'no':
                pass
            else:
                print('Provided response is not valid. Response must be "yes" or "no".')
                print('')
                keep_going = input('Configure another wordlist? ').lower()
        else:
            print('')
            print('Provided response is not valid. Response must be "yes" or "no".')
