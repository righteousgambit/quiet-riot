"""
Enumeration handlers for different scan types.
"""

import logging
import os
import re
import time
from typing import List, Optional, Tuple

import requests

from .enumeration import loadbalancer, s3aclenum

logger = logging.getLogger(__name__)


class EnumerationHandler:
    """Handles enumeration for different scan types."""

    def __init__(self, session):
        """
        Initialize enumeration handler.

        Args:
            session: Boto3 session object
        """
        self.session = session
        self.ms_url = "https://login.microsoftonline.com/common/GetCredentialType"

    def scan_aws_account_ids(self, wordlist_path: str, threads: int) -> Tuple[List[str], int]:
        """
        Scan for AWS Account IDs.

        Args:
            wordlist_path: Path to wordlist file
            threads: Number of threads to use

        Returns:
            Tuple of (valid_accounts, total_scanned)
        """
        logger.info("Starting AWS Account ID enumeration")
        results_file = loadbalancer.threader(
            loadbalancer.getter(thread=threads, wordlist=wordlist_path), session=self.session
        )

        # Load results
        valid_accounts = []
        if results_file and os.path.exists(results_file):
            with open(results_file) as f:
                valid_accounts = [line.strip() for line in f if line.strip()]

        total_scanned = self._count_wordlist_items(wordlist_path)
        return valid_accounts, total_scanned

    def scan_aws_iam_roles(self, wordlist_path: str, account_id: str, threads: int) -> Tuple[List[str], int]:
        """
        Scan for AWS IAM Roles.

        Args:
            wordlist_path: Path to wordlist file
            account_id: AWS Account ID to scan against
            threads: Number of threads to use

        Returns:
            Tuple of (valid_roles, total_scanned)
        """
        logger.info(f"Starting AWS IAM Role enumeration for account {account_id}")

        # Convert wordlist items to ARNs
        with open(wordlist_path) as f:
            role_names = [x.rstrip() for x in f]

        arn_list = [f"arn:aws:iam::{account_id}:role/{item}" for item in role_names]

        # Create temporary wordlist file
        temp_wordlist = f"wordlist-roles-{int(time.time())}.txt"
        with open(temp_wordlist, "w") as f:
            for arn in arn_list:
                f.write(f"{arn}\n")

        try:
            results_file = loadbalancer.threader(
                loadbalancer.getter(thread=threads, wordlist=temp_wordlist), session=self.session
            )

            # Load results
            valid_roles = []
            if results_file and os.path.exists(results_file):
                with open(results_file) as f:
                    valid_roles = [line.strip() for line in f if line.strip()]

            return valid_roles, len(role_names)
        finally:
            # Cleanup temp file
            if os.path.exists(temp_wordlist):
                os.remove(temp_wordlist)

    def scan_aws_iam_users(self, wordlist_path: str, account_id: str, threads: int) -> Tuple[List[str], int]:
        """
        Scan for AWS IAM Users.

        Args:
            wordlist_path: Path to wordlist file
            account_id: AWS Account ID to scan against
            threads: Number of threads to use

        Returns:
            Tuple of (valid_users, total_scanned)
        """
        logger.info(f"Starting AWS IAM User enumeration for account {account_id}")

        # Convert wordlist items to ARNs
        with open(wordlist_path) as f:
            user_names = [x.rstrip() for x in f]

        arn_list = [f"arn:aws:iam::{account_id}:user/{item}" for item in user_names]

        # Create temporary wordlist file
        temp_wordlist = f"wordlist-users-{int(time.time())}.txt"
        with open(temp_wordlist, "w") as f:
            for arn in arn_list:
                f.write(f"{arn}\n")

        try:
            results_file = loadbalancer.threader(
                loadbalancer.getter(thread=threads, wordlist=temp_wordlist), session=self.session
            )

            # Load results
            valid_users = []
            if results_file and os.path.exists(results_file):
                with open(results_file) as f:
                    valid_users = [line.strip() for line in f if line.strip()]

            return valid_users, len(user_names)
        finally:
            # Cleanup temp file
            if os.path.exists(temp_wordlist):
                os.remove(temp_wordlist)

    def scan_aws_services_footprint(self, wordlist_path: str, account_id: str, threads: int) -> Tuple[List[str], int]:
        """
        Scan for AWS Services Footprinting.

        Args:
            wordlist_path: Path to wordlist file
            account_id: AWS Account ID to scan against
            threads: Number of threads to use

        Returns:
            Tuple of (valid_roles, total_scanned)
        """
        logger.info(f"Starting AWS Services Footprinting for account {account_id}")
        # Same as IAM roles scan
        return self.scan_aws_iam_roles(wordlist_path, account_id, threads)

    def scan_microsoft_365_domain(self, domain_name: str) -> Tuple[List[str], int]:
        """
        Check if Microsoft 365 domain exists.

        Args:
            domain_name: Domain name to check

        Returns:
            Tuple of (valid_domains, total_checked)
        """
        logger.info(f"Checking if Microsoft 365 domain {domain_name} exists...")

        url = f"https://login.microsoftonline.com/getuserrealm.srf?login=user@{domain_name}"
        try:
            response = requests.get(url)  # nosec B113
            response_text = response.text

            valid_managed = re.search('"NameSpaceType":"Managed",', response_text)
            valid_federated = re.search('"NameSpaceType":"Federated",', response_text)

            valid_domains = []
            if valid_managed:
                logger.info(f"SUCCESS: Domain {domain_name} exists. Domain is Managed.")
                valid_domains.append(domain_name)
            elif valid_federated:
                logger.info(f"SUCCESS: Domain {domain_name} exists. Domain is Federated.")
                valid_domains.append(domain_name)
            else:
                logger.info(f"Domain {domain_name} does not exist.")

            return valid_domains, 1
        except Exception as e:
            logger.error(f"Error checking domain {domain_name}: {e}")
            return [], 1

    def scan_aws_root_email(self, email: str) -> Tuple[List[str], int]:
        """
        Scan for AWS root account email.

        Args:
            email: Email address to check

        Returns:
            Tuple of (valid_emails, total_checked)
        """
        logger.info(f"Checking if {email} is a valid AWS root account email...")

        if s3aclenum.s3_acl_princ_checker(email, self.session) == "Pass":
            logger.info(f"Valid root account email found: {email}")
            return [email], 1
        return [], 1

    def scan_microsoft_365_user(self, email: str, timeout: Optional[int] = None) -> Tuple[List[str], int]:
        """
        Scan for Microsoft 365 user email.

        Args:
            email: Email address to check
            timeout: Timeout between requests in seconds

        Returns:
            Tuple of (valid_emails, total_checked)
        """
        logger.info(f"Checking Microsoft 365 user: {email}")

        try:
            body = f'{{"Username":"{email}"}}'
            response = requests.post(self.ms_url, data=body)  # nosec B113
            response_text = response.text

            valid_response = re.search('"IfExistsResult":0,', response_text)
            valid_response5 = re.search('"IfExistsResult":5,', response_text)
            valid_response6 = re.search('"IfExistsResult":6,', response_text)
            invalid_response = re.search('"IfExistsResult":1,', response_text)
            desktopsso_response = re.search(
                '{"DesktopSsoEnabled":true,"UserTenantBranding":null,"DomainType":3}', response_text
            )
            throttling = re.search('"ThrottleStatus":1', response_text)

            valid_emails = []

            if desktopsso_response and (not valid_response or valid_response5 or valid_response6):
                logger.warning(f"[!] {email:51} Result - Desktop SSO Enabled")
                valid_emails.append(email)
            elif invalid_response and not desktopsso_response:
                logger.debug(f"[-] {email:51} Result - Invalid Email Found")
            elif valid_response or valid_response5 or valid_response6:
                logger.info(f"[+] {email:53} Result - Valid Email Found")
                valid_emails.append(email)

            if throttling:
                logger.error("O365 is responding with false positives. Retry the scan in 1 minute.")
                raise Exception("O365 throttling detected")

            if timeout:
                time.sleep(int(timeout))

            return valid_emails, 1
        except Exception as e:
            logger.error(f"Error checking Microsoft 365 user {email}: {e}")
            return [], 1

    def scan_google_workspace_user(self, email: str) -> Tuple[List[str], int]:
        """
        Scan for Google Workspace user email.

        Args:
            email: Email address to check

        Returns:
            Tuple of (valid_emails, total_checked)
        """
        logger.info(f"Checking Google Workspace user: {email}")

        try:
            params = {"email": email}
            response = requests.get("https://mail.google.com/mail/gxlu", params=params)  # nosec B113
            response_cookies = response.cookies

            if len(response_cookies) == 1:
                logger.info(f"Valid Google Workspace user found: {email}")
                return [email], 1
            return [], 1
        except Exception as e:
            logger.debug(f"Error checking Google Workspace user {email}: {e}")
            return [], 1

    def _count_wordlist_items(self, wordlist_path: str) -> int:
        """Count items in wordlist file."""
        try:
            with open(wordlist_path) as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
