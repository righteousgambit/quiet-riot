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
import requests as o365request
import re

# Define ANSI escape sequence colors


# Requests user to provide required info to kick off scan
def words_type(wordlist_type):
    while True:

        if str(wordlist_type) == '1':
            return 'accounts', 'none'
        elif str(wordlist_type) == '2':
            return 'micro_domain', 'none'
        elif str(wordlist_type) == 'roles':
            account_no = input('Provide an Account ID to scan against: ')
            print('')
            return 'roles', str(account_no)
        elif str(wordlist_type) == '3':
            return 'root account', 'none'
        # elif str(wordlist_type) == '3':
        #     account_no = input('Provide an Account ID to scan against: ')
        #     print('')
        #     return 'footprint', str(account_no)
        elif str(wordlist_type) == '4':
            account_no = input('Provide an Account ID to scan against: ')
            print('')
            return 'roles', str(account_no)
        elif str(wordlist_type) == '5':
            print('')
            return 'micro_users', 'none'
        elif str(wordlist_type) == '6':
            account_no = input('Provide an Account ID to scan against: ')
            print('')
            return 'users', str(account_no)
        else:
            print('You did not enter a valid Scan type.')
            print('')
            wordlist_type = input("\033[0;31m" + 'Enter a number between 1-6 ' + "\033[0m").lower()


# Creates final wordlist based on type of scanning to be performed.
def words(input_args, wordlist_type, session,email_option,email_list_path,email_eight_type,domain_name,micro_single_email,micro_timeout,micro_location_email,micro_email_type_response,micro_domain_name):
    ms_url = 'https://login.microsoftonline.com/common/GetCredentialType'
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
            # elif wordlist_type == 'footprint':
            #     wordlist_file = os.path.dirname(__file__) + '/wordlists/service-linked-roles.txt'
            elif wordlist_type == "micro_domain":
                valid_domain = []
                domain_name = micro_domain_name
                print(f"[info] Checking if the {domain_name} exists...\n")
                url = (
                    f"https://login.microsoftonline.com/getuserrealm.srf?login=user@{domain_name}")
                request = o365request.get(url)
                # print(request)
                response = request.text
                # print(response)
                valid_response = re.search('"NameSpaceType":"Managed",', response)
                valid_response1 = re.search('"NameSpaceType":"Federated",', response)
                # if args.verbose:
                #     print(domain_name, request, response, valid_response)
                if valid_response:
                    print(f"[success] The listed domain {domain_name} exists. Domain is Managed.\n")
                    valid_domain.append(micro_domain_name)
                elif valid_response1:
                    print(f"[success] The listed domain {domain_name} exists. Domain is Federated.\n")
                    valid_domain.append(micro_domain_name)
                else:
                    print(f"[info] The listed domain {domain_name} does not exist.\n")
                print('')
                print("-----------Scaning Completed----------")
                print('')
                results_file = f'valid_scan_results-{timestamp}.txt'
                with open(results_file, 'a+') as f:
                    for i in valid_domain:
                        f.write("%s\n" % i)

                f.close()
                return results_file

            elif wordlist_type == 'root account' and email_option != 'seventh_type' and email_option != 'eighth_type':
                try:
                    wordlist_file = os.path.dirname(__file__) + '/wordlists/final_emails.txt'
                except Exception as f:
                    print(f)
                    print("Error while reading file: ", wordlist_file)

            elif wordlist_type == 'root account' and email_list_path != '' and email_option == 'seventh_type':
                try:
                    wordlist_file = email_list_path
                except Exception as f:
                    print(f)
                    print("Error while reading file: ", wordlist_file)

            #singel email handling
            elif wordlist_type == 'root account' and email_option == 'eighth_type' and email_eight_type != '':
                print('')
                print("Scanning for Potential Root Users")
                print('')
                print('Identified Root Account E-mail Addresses:')
                valid_emails = []
                my_list = []
                my_list.append(email_eight_type)

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

            elif wordlist_type == "micro_users" and micro_email_type_response == 'second_type':
                micro_email_list = []
                email = micro_single_email
                s = o365request.session()
                body = '{"Username":"%s"}' % email
                request = o365request.post(ms_url, data=body)
                response_dict = request.json()
                response = request.text
                valid_response = re.search('"IfExistsResult":0,', response)
                valid_response5 = re.search('"IfExistsResult":5,', response)
                valid_response6 = re.search('"IfExistsResult":6,', response)
                invalid_response = re.search('"IfExistsResult":1,', response)
                desktopsso_response = re.search(
                    '{"DesktopSsoEnabled":true,"UserTenantBranding":null,"DomainType":3}', response)
                throttling = re.search('"ThrottleStatus":1', response)
                # if args.verbose:
                #     print('\n', email, s, body, request, response_dict, response, valid_response,
                #           valid_response5, valid_response6, invalid_response, desktopsso_response, '\n')
                if desktopsso_response and not valid_response or valid_response5 or valid_response6:
                    a = email
                    b = " Result -  Desktop SSO Enabled [!]"
                    print(f'[!] {a:51} {b} ')
                    micro_email_list.append(a)
                if invalid_response and not desktopsso_response:
                    a = email
                    b = " Result - Invalid Email Found! [-]"
                    print( f"[-] {a:51} {b}")
                if valid_response or valid_response5 or valid_response6:
                    a = email
                    b = " Result -   Valid Email Found! [+]"
                    print(f"[+] {a:53} {b} ")
                    micro_email_list.append(a)
                if throttling:
                    print("\nResults suggest O365 is responding with false positives. Retry the scan in 1 minute.")
                    sys.exit()
                if micro_timeout is not None:
                    time.sleep(int(micro_timeout))
                print('')
                print("-----------Scaning Completed----------")
                print('')
                results_file = f'valid_scan_results-{timestamp}.txt'
                with open(results_file, 'a+') as f:
                    for i in micro_email_list:
                        f.write("%s\n" % i)

                f.close()
                return results_file


            elif wordlist_type == "micro_users" and micro_email_type_response == 'first_type':
                try:
                    wordlist_file = micro_location_email
                except Exception as f:
                    print(f)
                    print("Error while reading file: ", wordlist_file)

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
                # elif wordlist_type == 'footprint':
                #     for item in my_list:
                #         new_list.append('arn:aws:iam::' + account_no + ':role/' + item)
                #     with open(wordlist, 'a+') as f:
                #         for item in new_list:
                #             f.write("%s\n" % item)
                #     # Configure user-defined wordlist as roles for triggering via enumeration.loadbalancer.threader(getter())
                #     results_file = loadbalancer.threader(
                #         loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session)
                #     return results_file
                #     break
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
                elif wordlist_type == 'root account' and email_option == 'seventh_type':
                    valid_emails = []
                    print('')
                    print("Scanning for Potential Root Users")
                    print('')
                    print('Identified Root Account E-mail Addresses:')

                    for username in my_list:
                        email = username.replace(' ','').lower() + '@' + str(domain_name)
                        if s3aclenum.s3_acl_princ_checker(str(email), session) == 'Pass':
                            print(str(email) + " is a root account")
                            print("")
                            valid_emails.append(email)
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

                elif wordlist_type == 'root account' and email_option != 'seventh_type' and email_option != 'eight_type':
                    valid_emails = []
                    print('')
                    print("Scanning for Potential Root Users")
                    print('')
                    print('Identified Root Account E-mail Addresses:')

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
                    print('')
                    delete_files = input('Do you want to delete the wordlist to save space(yes/no)? ').lower()
                    print('')
                    while True:

                        if delete_files == 'yes':
                            try:

                                comined_male_names = os.path.dirname(__file__) + '/wordlists/combined_male_names.txt'
                                os.remove(comined_male_names)

                            except Exception as com_male:
                                print("Error in deleting Combined male names file")
                                pass
                            try:

                                comined_female_names = os.path.dirname(__file__) + '/wordlists/combined_female_names.txt'
                                os.remove(comined_female_names)

                            except Exception as com_male:
                                print("Error in deleting comined_female_names file")
                                pass
                            try:

                                quiet_riot_names = os.path.dirname(__file__) + '/wordlists/names_quit_riot.txt'
                                os.remove(quiet_riot_names)

                            except Exception as com_male:
                                print("Error in deleting quiet_riot_names file")
                                pass
                            try:

                                comined_final_names = os.path.dirname(__file__) + '/wordlists/final_emails.txt'
                                os.remove(comined_final_names)

                            except Exception as com_male:
                                print("Error in deleting comined_final_names file")
                                pass
                            break
                        elif delete_files == 'no':
                            break
                        else:
                            break
                    results_file = f'valid_scan_results-{timestamp}.txt'
                    with open(results_file, 'a+') as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)

                    f.close()
                    return results_file
                    break


                elif wordlist_type == "micro_users" and micro_email_type_response == 'first_type':
                    counter = 0
                    timeout_counter = 0
                    valid_emails = []
                    for line in my_list:
                        s = o365request.session()
                        email_line = line.split()
                        email = ' '.join(email_line)
                        body = '{"Username":"%s"}' % email
                        request = o365request.post(ms_url, data=body)
                        response = request.text
                        valid_response = re.search('"IfExistsResult":0,', response)
                        valid_response5 = re.search('"IfExistsResult":5,', response)
                        valid_response6 = re.search('"IfExistsResult":6,', response)
                        invalid_response = re.search('"IfExistsResult":1,', response)
                        throttling = re.search('"ThrottleStatus":1', response)
                        desktopsso_response = re.search(
                            '{"DesktopSsoEnabled":true,"UserTenantBranding":null,"DomainType":3}', response)
                        # if args.verbose:
                        #     print('\n', s, email_line, email, body, request, response, valid_response,
                        #           valid_response5, valid_response6, invalid_response, desktopsso_response, '\n')
                        if desktopsso_response:
                            a = email
                            b = " Result -  Desktop SSO Enabled [!]"
                            print( f'[!] {a:51} {b} ')
                            valid_emails.append(a)
                        if invalid_response and not desktopsso_response:
                            a = email
                            b = " Result - Invalid Email Found! [-]"
                            print(f"[-] {a:51} {b}" )
                        if valid_response or valid_response5 or valid_response6:
                            a = email
                            b = " Result -   Valid Email Found! [+]"
                            print(f"[+] {a:51} {b}")
                            valid_emails.append(a)
                            counter = counter + 1

                        if throttling:
                            if micro_timeout is not None:
                                timeout_counter = timeout_counter + 1
                                if timeout_counter == 5:
                                    print(f'\n[warn] Results suggest O365 is responding with false positives.')
                                    print(f'\n[warn] Office365 has returned five false positives.\n')
                                    print(f'quiet_riot setting the wait time to 10 minutes. You can exit or allow the program to continue running.')
                                    time.sleep(int(300))
                                    print(f'\nScanning will continue in 5 minutes.')
                                    time.sleep(int(270))
                                    print(f'\nContinuing scan in 30 seconds.')
                                    time.sleep(int(30))
                                    timeout_counter = 0
                                    # sys.exit()
                                else:
                                    print(f"\n[warn] Results suggest O365 is responding with false positives. Sleeping for {micro_timeout} seconds before trying again.\n")
                                    time.sleep(int(micro_timeout))

                            else:
                                print("\n[warn] Results suggest O365 is responding with false positives. Restart scan and provide timeout to slow request times.")
                                sys.exit()
                        if micro_timeout is not None:
                            time.sleep(int(micro_timeout))
                    if counter == 0:
                        print( '\nThere were no valid logins found.')
                    elif counter == 1:
                        print('\nQuiet Riot discovered one valid login account.')
                    else:
                        print(f'\nQuiet Riot discovered {counter} valid login accounts.\n')

                    print('')
                    print("-----------Scaning Completed----------")
                    print('')

                    results_file = f'valid_scan_results-{timestamp}.txt'
                    with open(results_file, 'a+') as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)

                    f.close()
                    return results_file


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

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,prog='quiet_riot' , usage=' %(prog)s [--help,--h help] [--scan,--s SCAN] [--threads,--t THREADS] [--wordlist,--w WORDLIST] [--profile,--p PROFILE]')
    parser.add_argument('--scan', '--s', required=True, type=int, default=1,
                        help=textwrap.dedent('''\
                        What type of scan do you want to attempt? Enter the type of scan for example
                             1. AWS Account IDs
                             2. Microsoft 365 Domains
                             3. AWS Root User E-mail Address
                             4. AWS IAM Principals
                                4.1. IAM Roles
                                4.2. IAM Users
                             5. Microsoft 365 Users

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
    micro_domain_name = ''
    if wordlist_type == '2':

        print('')
        micro_domain_name = input("Domain Name to check for O365:  ")
        print('')
        while True:

            if micro_domain_name != '':
                micro_domain_name = micro_domain_name
                break

            else:
                print('')
                micro_domain_name = input("Domain Name to check for O365:  ")
                print('')
    def email_type():

        print(
            "E-mail Format (First and Last Names):\na. [first]@[domain]\nb. [first][last]@[domain]\nc. [first].[last]@[domain]\nd. [last]@[domain]\ne. [first]_[last]@[domain]\nf. [first_initial][last]@[domain]\ng. custom username list\nh. input single e-mail address\n")
        email_type_text = input("Enter an alphabet between a-h : ").lower()
        while True:

            if str(email_type_text) == 'a':
                return 'first_type'
            elif str(email_type_text) == 'b':
                return 'second_type'
            elif str(email_type_text) == 'c':
                return 'third_type'
            elif str(email_type_text) == 'd':
                return 'fourth_type'
            elif str(email_type_text) == 'e':
                return 'fifth_type'
            elif str(email_type_text) == 'f':
                return 'sixth_type'
            elif str(email_type_text) == 'g':
                return 'seventh_type'
            elif str(email_type_text) == 'h':
                return 'eighth_type'

            else:
                print('You did not enter a valid input.')
                print('')
                email_type_text = input("Enter an alphabet between a-h : ").lower()
                print('')

    def email_creation(email_option):

        family_names = os.path.dirname(__file__) + '/wordlists/familynames-usa-top1000.txt'

        female_name = os.path.dirname(__file__) + '/wordlists/femalenames-usa-top1000.txt'

        male_name = os.path.dirname(__file__) + '/wordlists/malenames-usa-top1000.txt'


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

        female_file = os.path.dirname(__file__) + '/wordlists/combined_female_names.txt'
        with open(female_file, 'w') as female_file:
            for i in combined_female_name:
                female_file.write(str(i) + '\n')

        female_file.close()

        combined_male_name = []
        for fam_name in family_names_list:

            for m_name in male_names_list:
                male_final_name = m_name + " " + fam_name

                combined_male_name.append(male_final_name)

        male_file = os.path.dirname(__file__) + '/wordlists/combined_male_names.txt'
        with open(male_file, 'w') as male_file:
            for i in combined_male_name:
                male_file.write(str(i) + '\n')

        male_file.close()

        random_final_names = combined_female_name + combined_male_name

        final_file = os.path.dirname(__file__) + '/wordlists/names_quit_riot.txt'
        with open(final_file, 'w') as final_file:
            for i in random_final_names:
                final_file.write(str(i) + '\n')

        final_file.close()

        email_list = []
        print('')
        domain_name = input("Domain Name:  ")
        print('')

        while True:

            if domain_name != '':
                domain_name = domain_name
                break

            else:
                print('')
                domain_name = input("Domain Name:  ")
                print('')

        for name in random_final_names:

            name = name.lower()
            if str(email_option) == 'first_type':
                email = name.split(" ")[0] + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == 'second_type':

                email = name.replace(" ", "") + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == 'third_type':

                email = name.replace(" ", ".") + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == 'fourth_type':

                email = name.split(" ")[1] + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == 'fifth_type':

                email = name.replace(" ", "_") + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == 'sixth_type':

                email = str(name[0]) + name.split(" ")[1] + "@" + str(domain_name)
                email_list.append(email)
        email_list_set = set(email_list)

        email_set_list = (list(email_list_set))

        final_email = os.path.dirname(__file__) + '/wordlists/final_emails.txt'
        with open(final_email, 'w') as final_file:
            for i in email_set_list:
                final_file.write(str(i) + '\n')
        print("Total Number of e-mail addresses generated: " + str(len(email_set_list)))
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
                wordlist_type = "6"
                return wordlist_type

            else:
                print('You did not enter a valid wordlist type.')
                print('')
                sub_iam_type = str(input("Enter a number 1 or 2 : "))

        # print(str(wordlist_type))

    if str(wordlist_type) == "4":
        wordlist_type = sub_scan_type()

    email_list_path = ''
    email_eight_type = ''
    domain_name = ''
    email_option = ''
    if str(wordlist_type) == "3":
        email_option = email_type()
        if str(email_option) == 'seventh_type':
            print('')
            email_list_path = input("Location to emails list file: ")
            print('')
            print('')
            domain_name = input("Domain Name:  ")
            print('')
            while True:

                if email_list_path != '':
                    email_list_path = email_list_path
                    break

                else:
                    print('')
                    email_list_path = input("Location to emails list file: ")
                    print('')

            while True:

                if domain_name != '':
                    domain_name = domain_name
                    break

                else:
                    print('')
                    domain_name = input("Domain Name:  ")
                    print('')

        elif str(email_option) == 'eighth_type':
            print('')
            email_eight_type = input("Enter full e-mail address: ").lower()
            print('')

            while True:

                if email_eight_type != '':
                    email_eight_type = email_eight_type
                    break

                else:
                    print('')
                    email_eight_type = input("Enter full e-mail address: ").lower()
                    print('')

        else:
            email_creation(email_option)
    def micro_email_type():

        print(
            "Validate a list of e-mails or single e-mail:\na. Custom e-mail list\nb. Input single e-mail address\n")
        email_type_text = input("Enter an alphabet(a/b): ").lower()
        while True:

            if str(email_type_text) == 'a':
                return 'first_type'
            elif str(email_type_text) == 'b':
                return 'second_type'

            else:
                print('You did not enter a valid input.')
                print('')
                email_type_text = input("Enter an alphabet(a/b): ").lower()
                print('')

    micro_single_email = ''
    micro_location_email = ''
    micro_timeout = None
    micro_email_type_response = ''
    if str(wordlist_type) == '5':
        micro_email_type_response = micro_email_type()
        if micro_email_type_response == 'second_type':

            print('')
            micro_single_email = input("Enter full e-mail address: ")
            print('')

            while True:

                if micro_single_email != '':
                    micro_single_email = micro_single_email
                    break

                else:
                    print('')
                    micro_single_email = input("Enter full e-mail address: ")
                    print('')

        elif micro_email_type_response == 'first_type':

            print('')
            micro_location_email = input("Location to emails list file: ")
            print('')

            while True:

                if micro_location_email != '':
                    micro_location_email = micro_location_email
                    break

                else:
                    print('')
                    micro_location_email = input("Location to emails list file: ")
                    print('')

        micro_timeout = input("Provide the timeout between requests in sec: ")
        print('')
        if micro_timeout == '':
            micro_timeout = None

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

    results_file = words(input_args, wordlist_type, session,email_option,email_list_path,email_eight_type,domain_name,micro_single_email,micro_timeout,micro_location_email,micro_email_type_response,micro_domain_name)
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
                        try:
                            # print("Deleting Quiet Riot Infrastructure: " + buckets['Buckets'][i]['Name'])
                            s3.delete_bucket(Bucket=buckets['Buckets'][i]['Name'])
                        except Exception:
                            pass
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
