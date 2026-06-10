"""
Core scanner implementation for Quiet Riot.
"""

from datetime import datetime
import logging
import os
from pathlib import Path
import time
import uuid

import boto3

from .. import config
from .enumeration import resource_manager
from .enumeration_handlers import EnumerationHandler
from .models import ScanConfig, ScanResult, ScanType
from .result_handler import ResultHandler
from .wordlist_handler import WordlistHandler

logger = logging.getLogger(__name__)


class Scanner:
    """Main scanner class for executing enumeration scans."""

    def __init__(self, session: boto3.Session):
        """
        Initialize scanner with AWS session.

        Args:
            session: Boto3 session object
        """
        self.session = session
        self.cfg = config.get_config()
        self.cfg.init(session)
        self.resource_mgr = resource_manager.ResourceManager(session)
        self.enumeration_handler = EnumerationHandler(session)
        self.wordlist_handler = WordlistHandler()
        self.result_handler = ResultHandler()

    def _setup_resources(self) -> tuple:
        """
        Set up AWS resources needed for scanning.

        Returns:
            Tuple of (ecr_public_repo, ecr_private_repo, sns_topic, s3_bucket, canonical_id)
        """
        logger.info("Setting up AWS resources for scanning...")

        ecr_public = self.session.client("ecr-public")
        ecr_private = self.session.client("ecr")
        sns = self.session.client("sns")
        s3 = self.session.client("s3")

        # Create ECR Public Repository
        ecr_public_repo = f"quiet-riot-public-repo-{uuid.uuid4().hex}"
        ecr_public.create_repository(repositoryName=ecr_public_repo)

        # Create ECR Private Repository
        ecr_private_repo = f"quiet-riot-private-repo-{uuid.uuid4().hex}"
        ecr_private.create_repository(repositoryName=ecr_private_repo)

        # Create SNS Topic
        sns_topic = f"quiet-riot-sns-topic-{uuid.uuid4().hex}"
        sns.create_topic(Name=sns_topic)

        # Create S3 Bucket
        s3_bucket = f"quiet-riot-bucket-{uuid.uuid4().hex}"
        s3.create_bucket(Bucket=s3_bucket)

        canonical_id = s3.list_buckets()["Owner"]["ID"]

        # Track resources
        self.resource_mgr.create_resources(ecr_public_repo, ecr_private_repo, sns_topic, s3_bucket, canonical_id)

        # Add to config
        self.cfg.add_scan_object(ecr_public_repo)
        self.cfg.add_scan_object(ecr_private_repo)
        sns_topic_arn = f"arn:aws:sns:us-east-1:{self.cfg.account_no}:{sns_topic}"
        self.cfg.add_scan_object(sns_topic_arn)
        self.cfg.add_scan_object(s3_bucket)
        self.cfg.add_scan_object(canonical_id)

        logger.info("AWS resources created successfully")
        return ecr_public_repo, ecr_private_repo, sns_topic, s3_bucket, canonical_id

    def _prepare_wordlist(self, scan_config: ScanConfig) -> tuple[str | None, str | None]:
        """
        Prepare wordlist for scanning based on scan type.

        Args:
            scan_config: Scan configuration

        Returns:
            Tuple of (wordlist_path, account_id)
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        base_dir = Path(__file__).parent.parent.parent

        if scan_config.scan_type == ScanType.AWS_ACCOUNT_IDS:
            # Generate random account IDs
            # Note: rand_id_generator prompts for input, so we handle this in run_scan
            # For CLI, the wordlist should be provided or generated beforehand
            if scan_config.wordlist_path:
                return scan_config.wordlist_path, None
            # Generate a default wordlist
            from .enumeration import rand_id_generator

            wordlist_file = rand_id_generator.rand_id_generator()
            return wordlist_file, None

        elif scan_config.scan_type == ScanType.AWS_SERVICES_FOOTPRINTING:
            # Use service-linked-roles wordlist
            wordlist_path = base_dir / "wordlists" / "service-linked-roles.txt"
            if not wordlist_path.exists():
                raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")
            return str(wordlist_path), scan_config.account_id

        elif scan_config.scan_type in [
            ScanType.AWS_IAM_PRINCIPALS,
            ScanType.AWS_IAM_ROLES,
            ScanType.AWS_IAM_USERS,
        ]:
            if not scan_config.wordlist_path:
                raise ValueError("Wordlist path required for IAM principal scans")
            if not scan_config.account_id:
                raise ValueError("Account ID required for IAM principal scans")
            return scan_config.wordlist_path, scan_config.account_id

        elif scan_config.scan_type == ScanType.AWS_ROOT_USER_EMAIL:
            if scan_config.single_email:
                # Single email check
                return None, None
            elif scan_config.email_list_path:
                return scan_config.email_list_path, None
            else:
                # Use default wordlist
                wordlist_path = base_dir / "wordlists" / "final_emails.txt"
                if wordlist_path.exists():
                    return str(wordlist_path), None
                raise FileNotFoundError("No email wordlist available")

        elif scan_config.scan_type == ScanType.MICROSOFT_365_USERS:
            if scan_config.single_email:
                return None, None
            elif scan_config.wordlist_path:
                return scan_config.wordlist_path, None
            raise ValueError("Email or wordlist required for Microsoft 365 user scan")

        elif scan_config.scan_type == ScanType.GOOGLE_WORKSPACE_USERS:
            if not scan_config.wordlist_path:
                raise ValueError("Wordlist required for Google Workspace user scan")
            return scan_config.wordlist_path, None

        else:
            if scan_config.wordlist_path:
                return scan_config.wordlist_path, None
            raise ValueError(f"No wordlist preparation logic for scan type {scan_config.scan_type}")

    def run_scan(self, scan_config: ScanConfig, cleanup: bool = True) -> ScanResult:
        """
        Execute a scan operation.

        Args:
            scan_config: Configuration for the scan
            cleanup: Whether to cleanup resources after scan

        Returns:
            ScanResult object with scan results
        """
        scan_id = str(uuid.uuid4())
        start_time = datetime.now()

        logger.info(f"Starting scan {scan_id} of type {scan_config.scan_type}")

        # Setup resources (only for AWS scans that need them)
        needs_resources = scan_config.scan_type in [
            ScanType.AWS_ACCOUNT_IDS,
            ScanType.AWS_SERVICES_FOOTPRINTING,
            ScanType.AWS_IAM_PRINCIPALS,
            ScanType.AWS_IAM_ROLES,
            ScanType.AWS_IAM_USERS,
        ]

        try:
            if needs_resources:
                self._setup_resources()

            # Execute scan based on type
            valid_principals: list[str] = []
            total_scanned = 0

            if scan_config.scan_type == ScanType.AWS_ACCOUNT_IDS:
                wordlist_path, _ = self._prepare_wordlist(scan_config)
                if not wordlist_path:
                    raise ValueError("Wordlist path is required for AWS Account ID scan")
                valid_principals, total_scanned = self.enumeration_handler.scan_aws_account_ids(
                    wordlist_path, scan_config.threads
                )

            elif scan_config.scan_type == ScanType.AWS_SERVICES_FOOTPRINTING:
                wordlist_path, account_id = self._prepare_wordlist(scan_config)
                if not account_id:
                    raise ValueError("Account ID is required for AWS Services Footprinting")
                if not wordlist_path:
                    raise ValueError("Wordlist path is required for AWS Services Footprinting")
                valid_principals, total_scanned = self.enumeration_handler.scan_aws_services_footprint(
                    wordlist_path, account_id, scan_config.threads
                )

            elif scan_config.scan_type == ScanType.AWS_IAM_ROLES:
                wordlist_path, account_id = self._prepare_wordlist(scan_config)
                if not account_id:
                    raise ValueError("Account ID is required for AWS IAM Roles scan")
                if not wordlist_path:
                    raise ValueError("Wordlist path is required for AWS IAM Roles scan")
                valid_principals, total_scanned = self.enumeration_handler.scan_aws_iam_roles(
                    wordlist_path, account_id, scan_config.threads
                )

            elif scan_config.scan_type == ScanType.AWS_IAM_USERS:
                wordlist_path, account_id = self._prepare_wordlist(scan_config)
                if not account_id:
                    raise ValueError("Account ID is required for AWS IAM Users scan")
                if not wordlist_path:
                    raise ValueError("Wordlist path is required for AWS IAM Users scan")
                valid_principals, total_scanned = self.enumeration_handler.scan_aws_iam_users(
                    wordlist_path, account_id, scan_config.threads
                )

            elif scan_config.scan_type == ScanType.AWS_IAM_PRINCIPALS:
                # "IAM Principals" enumerates both roles and users from the wordlist.
                wordlist_path, account_id = self._prepare_wordlist(scan_config)
                if not account_id:
                    raise ValueError("Account ID is required for AWS IAM Principals scan")
                if not wordlist_path:
                    raise ValueError("Wordlist path is required for AWS IAM Principals scan")
                role_principals, role_count = self.enumeration_handler.scan_aws_iam_roles(
                    wordlist_path, account_id, scan_config.threads
                )
                user_principals, user_count = self.enumeration_handler.scan_aws_iam_users(
                    wordlist_path, account_id, scan_config.threads
                )
                valid_principals = role_principals + user_principals
                total_scanned = role_count + user_count

            elif scan_config.scan_type == ScanType.MICROSOFT_365_DOMAINS:
                if not scan_config.domain_name:
                    raise ValueError("Domain name required for Microsoft 365 domain scan")
                valid_principals, total_scanned = self.enumeration_handler.scan_microsoft_365_domain(
                    scan_config.domain_name
                )

            elif scan_config.scan_type == ScanType.AWS_ROOT_USER_EMAIL:
                if scan_config.single_email:
                    valid_principals, total_scanned = self.enumeration_handler.scan_aws_root_email(
                        scan_config.single_email
                    )
                else:
                    wordlist_path, _ = self._prepare_wordlist(scan_config)
                    if wordlist_path and os.path.exists(wordlist_path):
                        emails = self.wordlist_handler.load_wordlist(wordlist_path)
                        for email in emails:
                            valid, _ = self.enumeration_handler.scan_aws_root_email(email)
                            valid_principals.extend(valid)
                            total_scanned += 1
                    else:
                        raise ValueError("Email or wordlist path required for AWS Root User Email scan")

            elif scan_config.scan_type == ScanType.MICROSOFT_365_USERS:
                if scan_config.single_email:
                    valid_principals, total_scanned = self.enumeration_handler.scan_microsoft_365_user(
                        scan_config.single_email, scan_config.timeout
                    )
                else:
                    wordlist_path, _ = self._prepare_wordlist(scan_config)
                    if wordlist_path and os.path.exists(wordlist_path):
                        emails = self.wordlist_handler.load_wordlist(wordlist_path)
                        for email in emails:
                            valid, _ = self.enumeration_handler.scan_microsoft_365_user(email, scan_config.timeout)
                            valid_principals.extend(valid)
                            total_scanned += 1
                    else:
                        raise ValueError("Email or wordlist path required for Microsoft 365 Users scan")

            elif scan_config.scan_type == ScanType.GOOGLE_WORKSPACE_USERS:
                wordlist_path, _ = self._prepare_wordlist(scan_config)
                if not wordlist_path or not os.path.exists(wordlist_path):
                    raise ValueError("Wordlist path required for Google Workspace Users scan")
                emails = self.wordlist_handler.load_wordlist(wordlist_path)
                for email in emails:
                    valid, _ = self.enumeration_handler.scan_google_workspace_user(email)
                    valid_principals.extend(valid)
                    total_scanned += 1

            else:
                raise ValueError(f"Unsupported scan type: {scan_config.scan_type}")

            # Save results
            results_file = None
            if valid_principals:
                results_file = self.result_handler.save_results(valid_principals, scan_config.scan_type.value)

            end_time = datetime.now()
            status = "completed"

            result = ScanResult(
                scan_id=scan_id,
                scan_type=scan_config.scan_type,
                status=status,
                valid_principals=valid_principals,
                total_scanned=total_scanned,
                start_time=start_time,
                end_time=end_time,
                results_file=str(results_file) if results_file else None,
            )

            logger.info(f"Scan {scan_id} completed: {len(valid_principals)}/{total_scanned} valid principals found")
            return result

        except Exception as e:
            logger.exception(f"Error during scan: {e}")
            return ScanResult(
                scan_id=scan_id,
                scan_type=scan_config.scan_type,
                status="failed",
                valid_principals=[],
                total_scanned=0,
                start_time=start_time,
                end_time=datetime.now(),
                error=str(e),
            )
        finally:
            if cleanup and needs_resources:
                logger.info("Cleaning up AWS resources...")
                self.resource_mgr.cleanup_all(force=True)
