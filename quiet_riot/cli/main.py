#!/usr/bin/env python3
"""
CLI entry point for Quiet Riot.
"""

import argparse
import logging
from os import environ
import sys

from .. import config
from ..aws_credentials import get_credentials_manager
from ..core.models import ScanConfig, ScanType
from ..core.scanner import Scanner

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog="quiet-riot",
        description="Quiet Riot - Cloud Recon Tool",
        epilog="""
Examples:
  quiet-riot --scan 1 --threads 100 --profile default
  quiet-riot --scan 3 --wordlist wordlists/service-linked-roles.txt
        """,
    )

    parser.add_argument(
        "--scan",
        "--s",
        type=int,
        required=True,
        choices=[1, 2, 3, 4, 5, 6, 7],
        help="""Scan type:
  1. AWS Account IDs
  2. Microsoft 365 Domains
  3. AWS Services Footprinting
  4. AWS Root User E-mail Address
  5. AWS IAM Principals
  6. Microsoft 365 Users (e-mails)
  7. Google Workspace Users (e-mails)
        """,
    )

    parser.add_argument(
        "--threads",
        "--t",
        type=int,
        default=100,
        help="Number of threads to use for scanning (default: 100)",
    )

    parser.add_argument(
        "--wordlist",
        "--w",
        type=str,
        default=None,
        help="Path to wordlist file (required for some scan types)",
    )

    parser.add_argument(
        "--profile",
        "--p",
        type=str,
        default=None,
        help=("AWS profile name (preferred over --arn). If not provided, will try 'default' profile."),
    )

    parser.add_argument(
        "--arn",
        type=str,
        default=None,
        help=(
            "AWS IAM role ARN in full format "
            "(e.g., arn:aws:iam::123456789012:role/MyRole). "
            "A profile will be created automatically if it doesn't exist. "
            "Profile name takes precedence if both are provided."
        ),
    )

    parser.add_argument(
        "--account-id",
        type=str,
        default=None,
        help="AWS Account ID to scan against (required for some scan types)",
    )

    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Domain name (required for Microsoft 365 scans)",
    )

    parser.add_argument(
        "--log-level",
        "--l",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Set logging level",
    )

    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Do not clean up AWS resources after scanning",
    )

    return parser


def print_banner():
    """Print Quiet Riot banner."""
    banner = r"""
    ________        .__        __    __________.__        __
    \_____  \  __ __|__| _____/  |_  \______   \__| _____/  |_
     /  / \  \|  |  \  |/ __ \   __\  |       _/  |/  _ \   __/
    /   \_/.  \  |  /  \  ___/|  |    |    |   \  (  <_> )  |
    \_____\ \_/____/|__|\___  >__|    |____|_  /__|\____/|__|
           \__>             \/               \/
    """
    logger.info(banner)


def map_scan_type(scan_num: int) -> ScanType:
    """Map scan number to ScanType enum."""
    mapping = {
        1: ScanType.AWS_ACCOUNT_IDS,
        2: ScanType.MICROSOFT_365_DOMAINS,
        3: ScanType.AWS_SERVICES_FOOTPRINTING,
        4: ScanType.AWS_ROOT_USER_EMAIL,
        5: ScanType.AWS_IAM_PRINCIPALS,
        6: ScanType.MICROSOFT_365_USERS,
        7: ScanType.GOOGLE_WORKSPACE_USERS,
    }
    return mapping.get(scan_num, ScanType.AWS_ACCOUNT_IDS)


def main():
    """Main CLI entry point."""
    environ["PYTHONIOENCODING"] = "UTF-8"

    # Initialize configuration
    cfg = config.get_config()

    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()

    # Set log level if provided
    if args.log_level:
        cfg.set_log_level(args.log_level)

    logger.info(f"Starting Quiet Riot with arguments: {args}")

    # Print banner
    print_banner()

    # Create AWS session using credentials manager
    credentials_mgr = get_credentials_manager()
    profile_name_used = None

    try:
        # Prefer profile name over ARN
        if args.profile:
            # User explicitly provided a profile name
            session, profile_name_used = credentials_mgr.get_or_create_session(
                args.profile,
                prefer_profile=True,
            )
            logger.info(f"Using AWS profile: {profile_name_used}")
        elif args.arn:
            # User provided an ARN
            session, profile_name_used = credentials_mgr.get_or_create_session(
                args.arn,
                prefer_profile=False,
            )
            logger.info(f"Using AWS profile created from ARN: {profile_name_used}")
        else:
            # Try default profile
            try:
                session, profile_name_used = credentials_mgr.get_or_create_session(
                    "default",
                    prefer_profile=True,
                )
                logger.info(f"Using default AWS profile: {profile_name_used}")
            except Exception:
                logger.error(
                    "No AWS credentials provided. "
                    "Please use --profile <name> or --arn <arn> "
                    "to specify AWS credentials."
                )
                sys.exit(1)

        # Validate the session
        is_valid, error_or_arn = credentials_mgr.validate_session(session)
        if not is_valid:
            logger.error(f"Invalid AWS credentials: {error_or_arn}")
            sys.exit(1)

        logger.info(f"Authenticated as: {error_or_arn}")

    except ValueError as e:
        logger.error(f"Invalid credentials configuration: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to create AWS session: {e}")
        sys.exit(1)

    # Map scan type
    scan_type = map_scan_type(args.scan)

    # Create scan configuration
    scan_config = ScanConfig(
        scan_type=scan_type,
        threads=args.threads,
        wordlist_path=args.wordlist,
        aws_profile=profile_name_used or args.profile or "default",
        account_id=args.account_id,
        domain_name=args.domain,
        log_level=args.log_level,
    )

    # Validate configuration
    if scan_type in [ScanType.AWS_SERVICES_FOOTPRINTING, ScanType.AWS_IAM_PRINCIPALS] and not args.account_id:
        logger.error(f"Account ID is required for scan type {scan_type.value}")
        sys.exit(1)

    if scan_type == ScanType.MICROSOFT_365_DOMAINS and not args.domain:
        logger.error("Domain name is required for Microsoft 365 domain scan")
        sys.exit(1)

    # Initialize scanner
    scanner = Scanner(session)

    try:
        # Update config with cleanup preference
        scan_config.cleanup = not args.no_cleanup

        # Run scan
        result = scanner.run_scan(scan_config, cleanup=scan_config.cleanup)

        # Print results
        logger.info("\n" + "=" * 60)
        logger.info("Scan Summary:")
        logger.info(f"  Status: {result.status}")
        logger.info(f"  Valid Principals Found: {len(result.valid_principals)}")
        logger.info(f"  Total Scanned: {result.total_scanned}")
        if result.duration_seconds:
            logger.info(f"  Duration: {result.duration_seconds:.2f} seconds")
        if result.results_file:
            logger.info(f"  Results File: {result.results_file}")
        logger.info("=" * 60)

        if result.error:
            logger.error(f"Scan completed with errors: {result.error}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\nScan interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Fatal error during scan: {e}")
        sys.exit(1)
