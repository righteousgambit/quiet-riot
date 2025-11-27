#!/usr/bin/env python3
import argparse
import glob
import logging
import os
from os import environ
import re
import sys
import textwrap
import time
import uuid

import boto3
import requests as o365request

from quiet_riot.core.enumeration import loadbalancer as loadbalancer
from quiet_riot.core.enumeration import rand_id_generator as rand_id_generator
from quiet_riot.core.enumeration import resource_manager
from quiet_riot.core.enumeration import s3aclenum as s3aclenum

from . import (
    config,
    settings,  # For backward compatibility
)

# Get logger
logger = logging.getLogger(__name__)


# Requests user to provide required info to kick off scan
def words_type(wordlist_type):
    while True:
        if str(wordlist_type) == "1":
            return "accounts", "none"
        elif str(wordlist_type) == "2":
            return "micro_domain", "none"
        elif str(wordlist_type) == "roles":
            account_no = input("Provide an Account ID to scan against: ")
            logger.info("")
            return "roles", str(account_no)

        elif str(wordlist_type) == "3":
            account_no = input("Provide an Account ID to scan against: ")
            logger.info("")
            return "footprint", str(account_no)
        elif str(wordlist_type) == "4":
            return "root account", "none"

        elif str(wordlist_type) == "5":
            account_no = input("Provide an Account ID to scan against: ")
            print("")
            return "roles", str(account_no)
        elif str(wordlist_type) == "6":
            print("")
            return "micro_users", "none"
        elif str(wordlist_type) == "7":
            print("")
            return "gmail_user", "none"
        elif str(wordlist_type) == "8":
            account_no = input("Provide an Account ID to scan against: ")
            print("")
            return "users", str(account_no)
        else:
            logger.warning("You did not enter a valid Scan type.")
            logger.info("")
            wordlist_type = input("\033[0;31m" + "Enter a number between 1-6 " + "\033[0m").lower()


# Creates final wordlist based on type of scanning to be performed.
def words(
    input_args,
    wordlist_type,
    session,
    email_option,
    email_list_path,
    email_eight_type,
    domain_name,
    micro_single_email,
    micro_timeout,
    micro_location_email,
    micro_email_type_response,
    micro_domain_name,
):
    ms_url = "https://login.microsoftonline.com/common/GetCredentialType"
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    wordlist_type, account_no = words_type(wordlist_type)
    # print(wordlist_type)
    wordlist_path = "wordlist-" + wordlist_type + "-" + timestamp + ".txt"
    wordlist = os.path.join(os.getcwd(), wordlist_path)
    new_list = []
    while True:
        try:
            if wordlist_type == "accounts":
                response = rand_id_generator.rand_id_generator()
                wordlist_file = response
            elif wordlist_type == "footprint":
                wordlist_file = os.path.dirname(__file__) + "/wordlists/service-linked-roles.txt"
            elif wordlist_type == "micro_domain":
                valid_domain = []
                domain_name = micro_domain_name
                logger.info(f"Checking if the {domain_name} exists...")
                url = f"https://login.microsoftonline.com/getuserrealm.srf?login=user@{domain_name}"
                request = o365request.get(url)  # nosec B113
                response = request.text
                valid_response = re.search('"NameSpaceType":"Managed",', response)
                valid_response1 = re.search('"NameSpaceType":"Federated",', response)
                if valid_response:
                    logger.info(f"SUCCESS: The listed domain {domain_name} exists. Domain is Managed.")
                    valid_domain.append(micro_domain_name)
                elif valid_response1:
                    logger.info(f"SUCCESS: The listed domain {domain_name} exists. Domain is Federated.")
                    valid_domain.append(micro_domain_name)
                else:
                    logger.info(f"The listed domain {domain_name} does not exist.")
                logger.info("-----------Scanning Completed----------")
                results_file = f"valid_scan_results-{timestamp}.txt"
                with open(results_file, "a+") as f:
                    for i in valid_domain:
                        f.write("%s\n" % i)

                f.close()
                return results_file

            elif wordlist_type == "root account" and email_option != "seventh_type" and email_option != "eighth_type":
                try:
                    wordlist_file = os.path.dirname(__file__) + "/wordlists/final_emails.txt"
                except Exception as f:
                    logger.error(f"Error while reading file {wordlist_file}: {f}")

            elif wordlist_type == "root account" and email_list_path != "" and email_option == "seventh_type":
                try:
                    wordlist_file = email_list_path
                except Exception as f:
                    logger.error(f"Error while reading file {wordlist_file}: {f}")

            # single email handling
            elif wordlist_type == "root account" and email_option == "eighth_type" and email_eight_type != "":
                logger.info("Scanning for Potential Root Users")
                logger.info("Identified Root Account E-mail Addresses:")
                valid_emails = []
                my_list = []
                my_list.append(email_eight_type)

                for i in my_list:
                    if s3aclenum.s3_acl_princ_checker(i, session) == "Pass":
                        logger.info(str(i))
                        valid_emails.append(i)
                    else:
                        pass

                logger.info("-----------Scanning Completed----------")

                results_file = f"valid_scan_results-{timestamp}.txt"
                with open(results_file, "a+") as f:
                    for i in valid_emails:
                        f.write("%s\n" % i)

                f.close()
                return results_file

            elif wordlist_type == "micro_users" and micro_email_type_response == "second_type":
                micro_email_list = []
                email = micro_single_email
                s = o365request.session()
                body = '{"Username":"%s"}' % email
                request = o365request.post(ms_url, data=body)  # nosec B113
                response_dict = request.json()
                response = request.text
                valid_response = re.search('"IfExistsResult":0,', response)
                valid_response5 = re.search('"IfExistsResult":5,', response)
                valid_response6 = re.search('"IfExistsResult":6,', response)
                invalid_response = re.search('"IfExistsResult":1,', response)
                desktopsso_response = re.search(
                    '{"DesktopSsoEnabled":true,"UserTenantBranding":null,"DomainType":3}', response
                )
                throttling = re.search('"ThrottleStatus":1', response)
                # if args.verbose:
                #     print('\n', email, s, body, request, response_dict, response, valid_response,
                #           valid_response5, valid_response6, invalid_response, desktopsso_response, '\n')
                if desktopsso_response and not valid_response or valid_response5 or valid_response6:
                    a = email
                    b = " Result -  Desktop SSO Enabled [!]"
                    logger.warning(f"[!] {a:51} {b}")
                    micro_email_list.append(a)
                if invalid_response and not desktopsso_response:
                    a = email
                    b = " Result - Invalid Email Found! [-]"
                    logger.debug(f"[-] {a:51} {b}")
                if valid_response or valid_response5 or valid_response6:
                    a = email
                    b = " Result -   Valid Email Found! [+]"
                    logger.info(f"[+] {a:53} {b}")
                    micro_email_list.append(a)
                if throttling:
                    logger.error("Results suggest O365 is responding with false positives. Retry the scan in 1 minute.")
                    sys.exit()
                if micro_timeout is not None:
                    time.sleep(int(micro_timeout))
                logger.info("-----------Scanning Completed----------")
                results_file = f"valid_scan_results-{timestamp}.txt"
                with open(results_file, "a+") as f:
                    for i in micro_email_list:
                        f.write("%s\n" % i)

                f.close()
                return results_file

            elif wordlist_type == "micro_users" and micro_email_type_response == "first_type":
                try:
                    wordlist_file = micro_location_email
                except Exception as f:
                    logger.error(f"Error while reading file {wordlist_file}: {f}")

            else:
                if str(input_args.wordlist) == "":
                    wordlist_file = input("Provide the path to wordlist file : ")
                else:
                    wordlist_file = input_args.wordlist

            print("")
            with open(wordlist_file) as file:
                my_list = [x.rstrip() for x in file]
                file.close()
                if wordlist_type == "roles":
                    for item in my_list:
                        new_list.append("arn:aws:iam::" + account_no + ":role/" + item)
                    with open(wordlist, "a+") as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as roles for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session
                    )
                    # print(results_file)
                    return results_file

                elif wordlist_type == "footprint":
                    for item in my_list:
                        new_list.append("arn:aws:iam::" + account_no + ":role/" + item)
                    with open(wordlist, "a+") as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as roles for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session
                    )
                    return results_file

                elif wordlist_type == "users":
                    for item in my_list:
                        new_list.append("arn:aws:iam::" + account_no + ":user/" + item)
                    with open(wordlist, "a+") as f:
                        for item in new_list:
                            f.write("%s\n" % item)
                    # Configure user-defined wordlist as users for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session
                    )
                    return results_file

                # TODO: Separate root accounts and setup s3 ACL check for root e-mail. Determine if root e-mail is only enumerable using s3 ACL
                elif wordlist_type == "accounts":
                    for item in my_list:
                        new_list.append(item)
                    with open(wordlist, "a+") as f:
                        for item in new_list:
                            f.write("%s\n" % item)

                    # Configure user-defined wordlist as account IDs or root account e-mails for triggering via enumeration.loadbalancer.threader(getter())
                    results_file = loadbalancer.threader(
                        loadbalancer.getter(thread=input_args.threads, wordlist=wordlist), session=session
                    )
                    return results_file

                elif wordlist_type == "root account" and email_option == "seventh_type":
                    valid_emails = []
                    logger.info("Scanning for Potential Root Users")
                    logger.info("Identified Root Account E-mail Addresses:")

                    for username in my_list:
                        email = username.replace(" ", "").lower() + "@" + str(domain_name)
                        if s3aclenum.s3_acl_princ_checker(str(email), session) == "Pass":
                            logger.info(str(email))
                            valid_emails.append(email)
                        else:
                            pass
                    logger.info("-----------Scanning Completed----------")
                    results_file = f"valid_scan_results-{timestamp}.txt"
                    with open(results_file, "a+") as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)

                    f.close()
                    return results_file

                elif wordlist_type == "gmail_user":
                    valid_emails = []
                    gmail_counter = 0
                    logger.info("Scanning for G-Suite (Google Workspace) Users")
                    logger.info("Identified G-suite (Google Workspace) Users: ")

                    for username in my_list:
                        params = {
                            "email": username,
                        }
                        try:
                            response = o365request.get("https://mail.google.com/mail/gxlu", params=params)  # nosec B113
                            response_cookies = response.cookies
                            if len(response_cookies) == 0:
                                pass
                            elif len(response_cookies) == 1:
                                logger.info(username)
                                valid_emails.append(username)
                                gmail_counter = gmail_counter + 1
                        except Exception as gmail_exc:
                            logger.debug(f"Error checking Gmail user {username}: {gmail_exc}")
                            pass

                    logger.info("-----------Scanning Completed----------")
                    if gmail_counter == 0:
                        logger.info("There were no valid e-mails found.")
                    elif gmail_counter == 1:
                        logger.info("Quiet Riot discovered one valid e-mail account.")
                    else:
                        logger.info(f"Quiet Riot discovered {gmail_counter} valid e-mails.")
                    results_file = f"valid_scan_results-{timestamp}.txt"
                    with open(results_file, "a+") as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)

                    f.close()
                    return results_file

                elif (
                    wordlist_type == "root account" and email_option != "seventh_type" and email_option != "eight_type"
                ):
                    valid_emails = []
                    logger.info("Scanning for Potential Root Users")
                    logger.info("Identified Root Account E-mail Addresses:")

                    for i in my_list:
                        if s3aclenum.s3_acl_princ_checker(i, session) == "Pass":
                            logger.info(str(i))
                            valid_emails.append(i)
                        else:
                            pass
                    logger.info("-----------Scanning Completed----------")
                    delete_files = input("Do you want to delete the wordlist to save space(yes/no)? ").lower()
                    while True:
                        if delete_files == "yes":
                            try:
                                comined_male_names = os.path.dirname(__file__) + "/wordlists/combined_male_names.txt"
                                os.remove(comined_male_names)
                            except Exception as com_male:
                                logger.warning(f"Error in deleting Combined male names file: {com_male}")
                                pass
                            try:
                                comined_female_names = (
                                    os.path.dirname(__file__) + "/wordlists/combined_female_names.txt"
                                )
                                os.remove(comined_female_names)
                            except Exception as com_male:
                                logger.warning(f"Error in deleting combined_female_names file: {com_male}")
                                pass
                            try:
                                quiet_riot_names = os.path.dirname(__file__) + "/wordlists/names_quit_riot.txt"
                                os.remove(quiet_riot_names)
                            except Exception as com_male:
                                logger.warning(f"Error in deleting quiet_riot_names file: {com_male}")
                                pass
                            try:
                                comined_final_names = os.path.dirname(__file__) + "/wordlists/final_emails.txt"
                                os.remove(comined_final_names)
                            except Exception as com_male:
                                logger.warning(f"Error in deleting combined_final_names file: {com_male}")
                                pass
                            break
                        elif delete_files == "no":
                            break
                        else:
                            break
                    results_file = f"valid_scan_results-{timestamp}.txt"
                    with open(results_file, "a+") as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)

                    f.close()
                    return results_file
                    break

                elif wordlist_type == "micro_users" and micro_email_type_response == "first_type":
                    counter = 0
                    timeout_counter = 0
                    valid_emails = []
                    for line in my_list:
                        s = o365request.session()
                        email_line = line.split()
                        email = " ".join(email_line)
                        body = '{"Username":"%s"}' % email
                        request = o365request.post(ms_url, data=body)  # nosec B113
                        response = request.text
                        valid_response = re.search('"IfExistsResult":0,', response)
                        valid_response5 = re.search('"IfExistsResult":5,', response)
                        valid_response6 = re.search('"IfExistsResult":6,', response)
                        invalid_response = re.search('"IfExistsResult":1,', response)
                        throttling = re.search('"ThrottleStatus":1', response)
                        desktopsso_response = re.search(
                            '{"DesktopSsoEnabled":true,"UserTenantBranding":null,"DomainType":3}', response
                        )
                        # if args.verbose:
                        #     print('\n', s, email_line, email, body, request, response, valid_response,
                        #           valid_response5, valid_response6, invalid_response, desktopsso_response, '\n')
                        if desktopsso_response:
                            a = email
                            b = " Result -  Desktop SSO Enabled [!]"
                            logger.warning(f"[!] {a:51} {b}")
                            valid_emails.append(a)
                        if invalid_response and not desktopsso_response:
                            a = email
                            b = " Result - Invalid Email Found! [-]"
                            logger.debug(f"[-] {a:51} {b}")
                        if valid_response or valid_response5 or valid_response6:
                            a = email
                            b = " Result -   Valid Email Found! [+]"
                            logger.info(f"[+] {a:51} {b}")
                            valid_emails.append(a)
                            counter = counter + 1

                        if throttling:
                            if micro_timeout is not None:
                                timeout_counter = timeout_counter + 1
                                if timeout_counter == 5:
                                    logger.warning("Results suggest O365 is responding with false positives.")
                                    logger.warning("Office365 has returned five false positives.")
                                    logger.warning(
                                        "quiet_riot setting the wait time to 10 minutes. You can exit or allow the program to continue running."
                                    )
                                    time.sleep(300)
                                    logger.info("Scanning will continue in 5 minutes.")
                                    time.sleep(270)
                                    logger.info("Continuing scan in 30 seconds.")
                                    time.sleep(30)
                                    timeout_counter = 0
                                else:
                                    logger.warning(
                                        f"Results suggest O365 is responding with false positives. Sleeping for {micro_timeout} seconds before trying again."
                                    )
                                    time.sleep(int(micro_timeout))
                            else:
                                logger.error(
                                    "Results suggest O365 is responding with false positives. Restart scan and provide timeout to slow request times."
                                )
                                sys.exit()
                        if micro_timeout is not None:
                            time.sleep(int(micro_timeout))
                    if counter == 0:
                        logger.info("There were no valid logins found.")
                    elif counter == 1:
                        logger.info("Quiet Riot discovered one valid login account.")
                    else:
                        logger.info(f"Quiet Riot discovered {counter} valid login accounts.")

                    logger.info("-----------Scanning Completed----------")

                    results_file = f"valid_scan_results-{timestamp}.txt"
                    with open(results_file, "a+") as f:
                        for i in valid_emails:
                            f.write("%s\n" % i)

                    f.close()
                    return results_file

                else:
                    logger.warning("Scan type provided is not valid.")
                    wordlist_type = input(
                        "\033[0;31m"
                        + "Wordlist is intended to be accounts, roles, users, groups, or root account? "
                        + "\033[0m"
                    ).lower()

        except OSError as e:
            logger.error(f"Provided filename does not appear to exist: {e}")
            continue


# def scan_inst():


def main():
    """Main entry point for Quiet Riot."""
    # Initialize configuration and logging
    cfg = config.get_config()

    environ["PYTHONIOENCODING"] = "UTF-8"

    # Create timestamp in preferred format for wordlist files
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog="quiet_riot",
        usage=" %(prog)s [--help,--h help] [--scan,--s SCAN] [--threads,--t THREADS] [--wordlist,--w WORDLIST] [--profile,--p PROFILE]",
    )
    parser.add_argument(
        "--scan",
        "--s",
        required=True,
        type=int,
        default=1,
        help=textwrap.dedent(
            """\
                        What type of scan do you want to attempt? Enter the type of scan for example
                             1. AWS Account IDs
                             2. Microsoft 365 Domains
                             3. AWS Services Footprinting
                             4. AWS Root User E-mail Address
                             5. AWS IAM Principals
                                4.1. IAM Roles
                                4.2. IAM Users
                             6. Microsoft 365 Users (e-mails)
                             7. Google Workspace Users (e-mails)

                             """
        ),
    )

    parser.add_argument(
        "--threads",
        "--t",
        type=int,
        default=100,
        help=textwrap.dedent(
            """\
                        Approximately how many threads do you think you want to run?

                        """
        ),
    )

    parser.add_argument(
        "--wordlist",
        "--w",
        type=str,
        default="",
        help=textwrap.dedent(
            """\
                        Path to the world list file which will be required for scan

                        """
        ),
    )

    parser.add_argument(
        "--profile",
        "--p",
        type=str,
        default="default",
        help=textwrap.dedent(
            """Name of aws profile

                        """
        ),
    )

    parser.add_argument(
        "--log-level",
        "--l",
        type=str,
        default=None,
        help=textwrap.dedent(
            """Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

                        """
        ),
    )

    input_args = parser.parse_args()

    # Set log level if provided
    if input_args.log_level:
        cfg.set_log_level(input_args.log_level)

    logger.info(f"Input arguments: {input_args}")

    # Display banner
    logger.info(
        r"""
    ________        .__        __    __________.__        __
    \\_____  \\  __ __|__| _____/  |_  \\______   \\__| _____/  |_
     /  / \\  \\|  |  \\  |/ __ \\   __\\  |       _/  |/  _ \\   __/
    /   \\_/.  \\  |  /  \\  ___/|  |    |    |   \\  (  <_> )  |
    \\_____\\ \\_/____/|__|\\___  >__|    |____|_  /__|\\____/|__|
           \\__>             \\/               \\/
    """
    )
    aws_profile_name = input_args.profile

    session = boto3.Session(profile_name=f"{aws_profile_name}")
    # print(session)
    s3 = session.client("s3")
    sts = session.client("sts")
    iam = session.client("iam")
    sns = session.client("sns")
    ecrprivate = session.client("ecr")
    ecrpublic = session.client("ecr-public")

    wordlist_type = str(input_args.scan)
    micro_domain_name = ""
    if wordlist_type == "2":
        micro_domain_name = input("Domain Name to check for O365:  ")
        while True:
            if micro_domain_name != "":
                micro_domain_name = micro_domain_name
                break
            else:
                micro_domain_name = input("Domain Name to check for O365:  ")

    def email_type():
        logger.info(
            "E-mail Format (First and Last Names):\na. [first]@[domain]\nb. [first][last]@[domain]\nc. [first].[last]@[domain]\nd. [last]@[domain]\ne. [first]_[last]@[domain]\nf. [first_initial][last]@[domain]\ng. custom username list\nh. input single e-mail address\n"
        )
        email_type_text = input("Enter an alphabet between a-h : ").lower()
        while True:
            if str(email_type_text) == "a":
                return "first_type"
            elif str(email_type_text) == "b":
                return "second_type"
            elif str(email_type_text) == "c":
                return "third_type"
            elif str(email_type_text) == "d":
                return "fourth_type"
            elif str(email_type_text) == "e":
                return "fifth_type"
            elif str(email_type_text) == "f":
                return "sixth_type"
            elif str(email_type_text) == "g":
                return "seventh_type"
            elif str(email_type_text) == "h":
                return "eighth_type"

            else:
                logger.warning("You did not enter a valid input.")
                email_type_text = input("Enter an alphabet between a-h : ").lower()

    def email_creation(email_option):
        family_names = os.path.dirname(__file__) + "/wordlists/familynames-usa-top1000.txt"

        female_name = os.path.dirname(__file__) + "/wordlists/femalenames-usa-top1000.txt"

        male_name = os.path.dirname(__file__) + "/wordlists/malenames-usa-top1000.txt"

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

        female_file = os.path.dirname(__file__) + "/wordlists/combined_female_names.txt"
        with open(female_file, "w") as female_file:
            for i in combined_female_name:
                female_file.write(str(i) + "\n")

        female_file.close()

        combined_male_name = []
        for fam_name in family_names_list:
            for m_name in male_names_list:
                male_final_name = m_name + " " + fam_name

                combined_male_name.append(male_final_name)

        male_file = os.path.dirname(__file__) + "/wordlists/combined_male_names.txt"
        with open(male_file, "w") as male_file:
            for i in combined_male_name:
                male_file.write(str(i) + "\n")

        male_file.close()

        random_final_names = combined_female_name + combined_male_name

        final_file = os.path.dirname(__file__) + "/wordlists/names_quit_riot.txt"
        with open(final_file, "w") as final_file:
            for i in random_final_names:
                final_file.write(str(i) + "\n")

        final_file.close()

        email_list = []
        print("")
        domain_name = input("Domain Name:  ")
        print("")

        while True:
            if domain_name != "":
                domain_name = domain_name
                break

            else:
                domain_name = input("Domain Name:  ")

        for name in random_final_names:
            name = name.lower()
            if str(email_option) == "first_type":
                email = name.split(" ")[0] + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == "second_type":
                email = name.replace(" ", "") + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == "third_type":
                email = name.replace(" ", ".") + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == "fourth_type":
                email = name.split(" ")[1] + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == "fifth_type":
                email = name.replace(" ", "_") + "@" + str(domain_name)
                email_list.append(email)

            elif str(email_option) == "sixth_type":
                email = str(name[0]) + name.split(" ")[1] + "@" + str(domain_name)
                email_list.append(email)
        email_list_set = set(email_list)

        email_set_list = list(email_list_set)

        final_email = os.path.dirname(__file__) + "/wordlists/final_emails.txt"
        with open(final_email, "w") as final_file:
            for i in email_set_list:
                final_file.write(str(i) + "\n")
        logger.info(f"Total Number of e-mail addresses generated: {len(email_set_list)}")

    def sub_scan_type():
        logger.info("1. IAM Roles")
        logger.info("2. IAM Users")
        sub_iam_type = input("Kindly select one of the above scan types:")
        while True:
            if sub_iam_type == "1":
                wordlist_type = "5"
                return wordlist_type
            elif sub_iam_type == "2":
                wordlist_type = "8"
                return wordlist_type
            else:
                logger.warning("You did not enter a valid wordlist type.")
                sub_iam_type = str(input("Enter a number 1 or 2 : "))

        # print(str(wordlist_type))

    if str(wordlist_type) == "5":
        wordlist_type = sub_scan_type()

    email_list_path = ""
    email_eight_type = ""
    domain_name = ""
    email_option = ""
    if str(wordlist_type) == "4":
        email_option = email_type()
        if str(email_option) == "seventh_type":
            email_list_path = input("Location to emails list file: ")
            domain_name = input("Domain Name:  ")
            while True:
                if email_list_path != "":
                    email_list_path = email_list_path
                    break
                else:
                    email_list_path = input("Location to emails list file: ")

            while True:
                if domain_name != "":
                    domain_name = domain_name
                    break
                else:
                    domain_name = input("Domain Name:  ")

        elif str(email_option) == "eighth_type":
            email_eight_type = input("Enter full e-mail address: ").lower()
            while True:
                if email_eight_type != "":
                    email_eight_type = email_eight_type
                    break
                else:
                    email_eight_type = input("Enter full e-mail address: ").lower()

        else:
            email_creation(email_option)

    def micro_email_type():
        logger.info(
            "Validate a list of e-mails or single e-mail:\na. Custom e-mail list\nb. Input single e-mail address\n"
        )
        email_type_text = input("Enter an alphabet(a/b): ").lower()
        while True:
            if str(email_type_text) == "a":
                return "first_type"
            elif str(email_type_text) == "b":
                return "second_type"
            else:
                logger.warning("You did not enter a valid input.")
                email_type_text = input("Enter an alphabet(a/b): ").lower()

    micro_single_email = ""
    micro_location_email = ""
    micro_timeout = None
    micro_email_type_response = ""
    if str(wordlist_type) == "6":
        micro_email_type_response = micro_email_type()
        if micro_email_type_response == "second_type":
            micro_single_email = input("Enter full e-mail address: ")
            while True:
                if micro_single_email != "":
                    micro_single_email = micro_single_email
                    break
                else:
                    micro_single_email = input("Enter full e-mail address: ")

        elif micro_email_type_response == "first_type":
            micro_location_email = input("Location to emails list file: ")
            while True:
                if micro_location_email != "":
                    micro_location_email = micro_location_email
                    break
                else:
                    micro_location_email = input("Location to emails list file: ")

        micro_timeout = input("Provide the timeout between requests in sec: ")
        if micro_timeout == "":
            micro_timeout = None

    # Create s3 bucket to scan against for root account e-mail addresses.

    # global_bucket = 's3://quiet-riot-global-bucket/'

    # initialize
    #############################################################################
    ##                                                                         ##
    ##           Deployment of Enumeration Infra based on user preference      ##
    ##                                                                         ##
    #############################################################################

    # Initialize resource manager for proper cleanup
    resource_mgr = resource_manager.ResourceManager(session)

    # Create ECR Public Repository - Resource that has IAM policy attachment
    ecr_public_repo = f"quiet-riot-public-repo-{uuid.uuid4().hex}"
    ecrpublic.create_repository(repositoryName=ecr_public_repo)
    # Create ECR Private Repository - Resource that has IAM policy attachment
    ecr_private_repo = f"quiet-riot-private-repo-{uuid.uuid4().hex}"
    ecrprivate.create_repository(repositoryName=ecr_private_repo)
    # Create SNS Topic - Resource that has IAM policy attachment
    sns_topic = f"quiet-riot-sns-topic-{uuid.uuid4().hex}"
    sns.create_topic(Name=sns_topic)
    # Create s3 bucket to scan against for root account e-mail addresses.
    s3_bucket = f"quiet-riot-bucket-{uuid.uuid4().hex}"
    s3.create_bucket(Bucket=s3_bucket)

    canonical_id = s3.list_buckets()["Owner"]["ID"]

    # Track resources in resource manager
    resource_mgr.create_resources(ecr_public_repo, ecr_private_repo, sns_topic, s3_bucket, canonical_id)

    # Initialize config and add scan objects
    cfg.init(session)
    cfg.add_scan_object(ecr_public_repo)
    cfg.add_scan_object(ecr_private_repo)
    sns_topic_arn = f"arn:aws:sns:us-east-1:{cfg.account_no}:{sns_topic}"
    cfg.add_scan_object(sns_topic_arn)
    cfg.add_scan_object(s3_bucket)
    cfg.add_scan_object(canonical_id)

    # Backward compatibility - update settings module
    settings.init(session)

    # Call initial workflow that takes a user wordlist and starts a scan.
    account_arn = sts.get_caller_identity()["Arn"]

    # Use try/finally to ensure cleanup happens
    results_file = None
    try:
        results_file = words(
            input_args,
            wordlist_type,
            session,
            email_option,
            email_list_path,
            email_eight_type,
            domain_name,
            micro_single_email,
            micro_timeout,
            micro_location_email,
            micro_email_type_response,
            micro_domain_name,
        )
        # print(results_file)
        default_bucket_name = f"quiet-riot-{cfg.account_no}"

        buckets = s3.list_buckets()
        bucket_flag = 0

        for i in range(0, len(buckets["Buckets"])):
            if str(default_bucket_name) in buckets["Buckets"][i]["Name"]:
                bucket_flag = 1
                logger.info(f"S3 bucket is already there with this name: {default_bucket_name}")
                break
            else:
                bucket_flag = 0
                pass

        if bucket_flag == 0:
            logger.info(f"Creating S3 bucket for uploading results: {default_bucket_name}")
            s3_bucket = f"{str(default_bucket_name)}"
            s3.create_bucket(Bucket=s3_bucket, ACL="private")
            response_public = s3.put_public_access_block(
                Bucket=f"{str(default_bucket_name)}",
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )

            time.sleep(4)

        try:
            result_file_path = os.path.join(os.getcwd(), results_file)
            s3.put_object(
                Body=open(f"{result_file_path}", "rb"), Bucket=f"{default_bucket_name}", Key=f"{results_file}"
            )
            bucket_obj_url = s3.generate_presigned_url(
                "get_object", Params={"Bucket": default_bucket_name, "Key": results_file}, ExpiresIn=604800
            )
            logger.info("Download your scan results:")
            logger.info(bucket_obj_url)
        except Exception as result_exc:
            logger.error(f"Error uploading file to S3 bucket: {result_exc}")

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
    finally:
        # Always attempt cleanup, but make it configurable
        cleanup_resources = True

        # Ask user if they want to clean up infrastructure (default: yes)
        try:
            prompt = (
                input('Finished Scanning? Answer "yes" to delete your infrastructure (default: yes): ').lower().strip()
            )
            if prompt in ("", "yes", "y"):
                cleanup_resources = True
            elif prompt in ("no", "n"):
                cleanup_resources = False
                logger.info(
                    "\033[0;32mResources will remain. You can review your validated principals in the results file.\033[0m"
                )
            else:
                logger.warning("Invalid response. Defaulting to cleanup.")
        except (EOFError, KeyboardInterrupt):
            # If input is not available (e.g., in automated scripts), default to cleanup
            logger.info("Input not available. Proceeding with cleanup.")
            cleanup_resources = True

        if cleanup_resources:
            logger.info("Cleaning up AWS resources...")
            resource_mgr.cleanup_all(force=True)
            logger.info("Cleanup completed.")

        # Clean up local wordlist files
        try:
            fileList = glob.glob("wordlist-**")
            for filePath in fileList:
                try:
                    wordlist_file_path = os.path.join(os.getcwd(), filePath)
                    os.remove(wordlist_file_path)
                except Exception as text_file:
                    logger.warning(f"Error while deleting wordlist file {wordlist_file_path}: {text_file}")
        except Exception as wordlist_file_exc:
            logger.error(f"Error during wordlist cleanup: {wordlist_file_exc}")
