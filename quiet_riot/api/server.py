#!/usr/bin/env python3
"""
FastAPI server for Quiet Riot with dashboard UI.
"""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Dict, List, Optional

import boto3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .. import config
from ..aws_credentials import get_credentials_manager
from ..core.models import ScanConfig, ScanResult, ScanType
from ..core.scanner import Scanner

logger = logging.getLogger(__name__)

# Global scanner instance
scanner: Optional[Scanner] = None
active_scans: Dict[str, ScanResult] = {}
current_profile: Optional[str] = None
credentials_required: bool = False
# Track infrastructure resources across all scans
infrastructure_resources: Dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    global scanner, credentials_required, current_profile
    # Startup
    logger.info("Initializing Quiet Riot API server...")

    credentials_mgr = get_credentials_manager()

    # Try to create a default session
    try:
        session = boto3.Session()
        is_valid, arn_or_error = credentials_mgr.validate_session(session)
        if is_valid:
            scanner = Scanner(session)
            current_profile = "default"
            logger.info("FastAPI server started successfully with default credentials")
            logger.info(f"Authenticated as: {arn_or_error}")
            credentials_required = False
        else:
            logger.warning(f"Default AWS credentials are invalid: {arn_or_error}")
            logger.warning("AWS credentials required. Please provide credentials via /api/credentials endpoint")
            credentials_required = True
    except Exception as e:
        logger.warning(f"Could not initialize AWS session: {e}")
        logger.warning("AWS credentials required. Please provide credentials via /api/credentials endpoint")
        credentials_required = True

    yield

    # Shutdown
    logger.info("Shutting down Quiet Riot API server...")


app = FastAPI(
    title="Quiet Riot",
    description="Cloud Recon Tool - Enumeration tool for AWS, Azure, and GCP principals",
    version="1.0.7",
    lifespan=lifespan,
)

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent

from jinja2 import Environment, FileSystemLoader

jinja_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=True,
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class ScanRequest(BaseModel):
    """Request model for starting a scan."""

    scan_type: int
    threads: int = 100
    wordlist_path: Optional[str] = None
    aws_profile: Optional[str] = None
    aws_arn: Optional[str] = None
    account_id: Optional[str] = None
    domain_name: Optional[str] = None
    single_email: Optional[str] = None
    timeout: Optional[int] = None
    # Email-based scan options
    email_list: Optional[List[str]] = None
    email_domain: Optional[str] = None
    name_list: Optional[List[str]] = None
    # IAM-based scan options
    iam_list: Optional[List[str]] = None
    use_vendor_principals: Optional[bool] = False
    # Domain-based scan options
    domain_list: Optional[List[str]] = None
    # Account ID scan options
    account_id_list: Optional[List[str]] = None
    generate_account_ids: Optional[bool] = False
    account_id_count: Optional[int] = 1000


class CredentialsRequest(BaseModel):
    """Request model for setting AWS credentials."""

    profile: Optional[str] = None
    arn: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the main dashboard."""
    template = jinja_env.get_template("dashboard.html")
    return HTMLResponse(content=template.render())


@app.get("/api/scan-types")
async def get_scan_types():
    """Get available scan types."""
    return {
        "scan_types": [
            # AWS Scans
            {
                "id": 1,
                "name": "AWS Account IDs",
                "description": "Enumerate valid AWS account IDs",
                "requires_config": True,
            },
            {
                "id": 3,
                "name": "AWS Services Footprinting",
                "description": "Footprint AWS services",
                "requires_config": False,
            },
            {
                "id": 4,
                "name": "AWS Root User Email",
                "description": "Enumerate AWS root user email addresses",
                "requires_config": True,
                "email_based": True,
            },
            {
                "id": 5,
                "name": "AWS IAM Principals",
                "description": ("Enumerate AWS IAM principals (roles and users)"),
                "requires_config": True,
                "iam_based": True,
            },
            # Microsoft 365 Scans
            {
                "id": 2,
                "name": "Microsoft 365 Domains",
                "description": "Check if Microsoft 365 domain exists",
                "requires_config": True,
            },
            {
                "id": 6,
                "name": "Microsoft 365 Users",
                "description": "Enumerate Microsoft 365 user emails",
                "requires_config": True,
                "email_based": True,
            },
            # Google Workspace Scans
            {
                "id": 7,
                "name": "Google Workspace Users",
                "description": "Enumerate Google Workspace user emails",
                "requires_config": True,
                "email_based": True,
            },
        ]
    }


@app.post("/api/credentials")
async def set_credentials(credentials_request: CredentialsRequest):
    """Set AWS credentials for the API server."""
    global scanner, current_profile, credentials_required

    credentials_mgr = get_credentials_manager()

    try:
        # Prefer profile over ARN
        if credentials_request.profile:
            session, profile_name = credentials_mgr.get_or_create_session(
                credentials_request.profile,
                prefer_profile=True,
            )
        elif credentials_request.arn:
            session, profile_name = credentials_mgr.get_or_create_session(
                credentials_request.arn,
                prefer_profile=False,
            )
        else:
            raise HTTPException(status_code=400, detail="Either 'profile' or 'arn' must be provided")

        # Validate the session
        is_valid, arn_or_error = credentials_mgr.validate_session(session)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid AWS credentials: {arn_or_error}")

        # Update global scanner
        scanner = Scanner(session)
        current_profile = profile_name
        credentials_required = False

        return {
            "status": "success",
            "message": "Credentials configured successfully",
            "profile": profile_name,
            "arn": arn_or_error,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Error setting credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/credentials")
async def get_credentials_status():
    """Get current AWS credentials status."""
    global scanner, current_profile, credentials_required

    if scanner is None or credentials_required:
        return {
            "configured": False,
            "message": ("AWS credentials not configured. Please use POST /api/credentials to set credentials."),
            "required": True,
        }

    credentials_mgr = get_credentials_manager()
    is_valid, arn_or_error = credentials_mgr.validate_session(scanner.session)

    return {
        "configured": is_valid,
        "profile": current_profile,
        "arn": arn_or_error if is_valid else None,
        "required": credentials_required,
    }


@app.post("/api/scans")
async def start_scan(scan_request: ScanRequest):
    """Start a new scan."""
    global scanner, current_profile

    # Check if credentials are required
    if credentials_required and scanner is None:
        raise HTTPException(
            status_code=503,
            detail=("AWS credentials required. Please configure credentials via POST /api/credentials first."),
        )

    # If scan request specifies different credentials, use them
    scan_session = None
    if scan_request.aws_profile or scan_request.aws_arn:
        credentials_mgr = get_credentials_manager()
        try:
            if scan_request.aws_profile:
                scan_session, _ = credentials_mgr.get_or_create_session(
                    scan_request.aws_profile,
                    prefer_profile=True,
                )
            elif scan_request.aws_arn:
                scan_session, _ = credentials_mgr.get_or_create_session(
                    scan_request.aws_arn,
                    prefer_profile=False,
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid credentials in scan request: {e}") from e

    # Use scan-specific session if provided, otherwise use global scanner
    if scan_session:
        scan_scanner = Scanner(scan_session)
    elif scanner is None:
        raise HTTPException(status_code=503, detail="Scanner not initialized. Check AWS credentials.")
    else:
        scan_scanner = scanner

    try:
        scan_type = ScanType(str(scan_request.scan_type))

        # Handle wordlist generation based on scan type and configuration
        wordlist_path = scan_request.wordlist_path

        # Generate wordlist from provided data if needed
        if not wordlist_path:
            import random
            import tempfile

            # Create temporary wordlist file
            temp_dir = Path(tempfile.gettempdir()) / "quiet_riot"
            temp_dir.mkdir(exist_ok=True)

            if scan_type == ScanType.AWS_ACCOUNT_IDS:
                if scan_request.generate_account_ids:
                    # Generate account IDs programmatically
                    count = scan_request.account_id_count or 1000
                    wordlist_path = str(temp_dir / f"account_ids_{count}.txt")
                    with open(wordlist_path, "w") as f:
                        for _ in range(count):
                            # Generate random 12-digit account ID
                            account_id = random.randint(10**11, 10**12 - 1)
                            f.write(f"{account_id}\n")
                elif scan_request.account_id_list:
                    wordlist_path = str(temp_dir / "account_ids_custom.txt")
                    with open(wordlist_path, "w") as f:
                        for account_id in scan_request.account_id_list:
                            f.write(f"{account_id.strip()}\n")

            elif scan_type in [
                ScanType.AWS_ROOT_USER_EMAIL,
                ScanType.MICROSOFT_365_USERS,
                ScanType.GOOGLE_WORKSPACE_USERS,
            ]:
                if scan_request.email_list:
                    wordlist_path = str(temp_dir / "emails_custom.txt")
                    with open(wordlist_path, "w") as f:
                        for email in scan_request.email_list:
                            f.write(f"{email.strip()}\n")
                # Email list is already generated on the frontend
                # Just use it directly

            elif scan_type == ScanType.AWS_IAM_PRINCIPALS:
                if scan_request.iam_list:
                    wordlist_path = str(temp_dir / "iam_principals_custom.txt")
                    with open(wordlist_path, "w") as f:
                        for iam in scan_request.iam_list:
                            f.write(f"{iam.strip()}\n")
                elif scan_request.use_vendor_principals:
                    # Use common vendor principals from wordlist
                    vendor_file = Path(__file__).parent.parent.parent.parent / "wordlists" / "service-linked-roles.txt"
                    if vendor_file.exists():
                        wordlist_path = str(vendor_file)
                    else:
                        msg = "Vendor principals wordlist not found"
                        raise HTTPException(status_code=400, detail=msg)

            elif scan_type == ScanType.MICROSOFT_365_DOMAINS and scan_request.domain_list:
                wordlist_path = str(temp_dir / "domains.txt")
                with open(wordlist_path, "w") as f:
                    for domain in scan_request.domain_list:
                        f.write(f"{domain.strip()}\n")

        # Determine profile name for scan config
        profile_name = current_profile or "default"
        if scan_request.aws_profile:
            profile_name = scan_request.aws_profile
        elif scan_request.aws_arn:
            # Get profile name from ARN
            credentials_mgr = get_credentials_manager()
            if credentials_mgr.is_arn(scan_request.aws_arn):
                arn_info = credentials_mgr.parse_arn(scan_request.aws_arn)
                if arn_info["resource_name"]:
                    profile_name = f"qr-{arn_info['account_id']}-{arn_info['resource_name']}"
                else:
                    profile_name = f"qr-{arn_info['account_id']}-{arn_info['resource_type']}"

        scan_config = ScanConfig(
            scan_type=scan_type,
            threads=scan_request.threads,
            wordlist_path=wordlist_path,
            aws_profile=profile_name,
            account_id=scan_request.account_id,
            domain_name=scan_request.domain_name,
            single_email=(scan_request.single_email if hasattr(scan_request, "single_email") else None),
            timeout=scan_request.timeout if hasattr(scan_request, "timeout") else None,
        )

        # Run scan (synchronous for now - can be made async later)
        # In production, this should run in a background task
        # Don't cleanup immediately - let user manage cleanup via UI
        result = scan_scanner.run_scan(scan_config, cleanup=False)
        active_scans[result.scan_id] = result

        # Track infrastructure resources created for this scan
        if scan_scanner.resource_mgr.resources_created:
            infrastructure_resources[result.scan_id] = {
                "ecr_public_repo": scan_scanner.resource_mgr.ecr_public_repo,
                "ecr_private_repo": scan_scanner.resource_mgr.ecr_private_repo,
                "sns_topic_arn": scan_scanner.resource_mgr.sns_topic_arn,
                "s3_bucket": scan_scanner.resource_mgr.s3_bucket,
                "canonical_id": scan_scanner.resource_mgr.canonical_id,
                "scan_id": result.scan_id,
                "scan_type": result.scan_type.value,
                "created_at": result.start_time.isoformat(),
            }

        return {
            "scan_id": result.scan_id,
            "status": result.status,
            "message": ("Scan completed successfully" if result.status == "completed" else "Scan failed"),
            "valid_principals_count": len(result.valid_principals),
            "total_scanned": result.total_scanned,
        }
    except ValueError as e:
        logger.warning(f"Invalid scan request: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Error starting scan: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/scans/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get status of a scan."""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="Scan not found")

    result = active_scans[scan_id]
    return {
        "scan_id": result.scan_id,
        "scan_type": result.scan_type.value,
        "status": result.status,
        "valid_principals_count": len(result.valid_principals),
        "total_scanned": result.total_scanned,
        "success_rate": result.success_rate,
        "duration_seconds": result.duration_seconds,
        "start_time": result.start_time.isoformat(),
        "end_time": result.end_time.isoformat() if result.end_time else None,
        "error": result.error,
    }


@app.get("/api/scans")
async def list_scans():
    """List all scans."""
    return {
        "scans": [
            {
                "scan_id": result.scan_id,
                "scan_type": result.scan_type.value,
                "status": result.status,
                "start_time": result.start_time.isoformat(),
            }
            for result in active_scans.values()
        ]
    }


@app.get("/api/generate-emails")
async def generate_emails(
    domain: str,
    pattern: str,
    max_emails: int = 1000,
):
    """
    Generate email addresses from wordlists using common patterns.

    Args:
        domain: Domain name for emails
        pattern: Email pattern (e.g., "firstname.lastname", "firstnamelastname")
        max_emails: Maximum number of emails to generate (default: 1000, max: 20,000,000)

    Returns:
        List of generated email addresses
    """
    # Limit max emails to 20 million
    max_emails = min(max_emails, 20_000_000)

    # Wordlists are in the project root
    # Path: quiet_riot/api/server.py -> quiet_riot/ -> project root
    wordlists_dir = Path(__file__).parent.parent.parent / "wordlists"

    # Load wordlists
    try:
        with open(wordlists_dir / "femalenames-usa-top1000.txt") as f:
            female_names = [line.strip().lower() for line in f if line.strip()]
        with open(wordlists_dir / "malenames-usa-top1000.txt") as f:
            male_names = [line.strip().lower() for line in f if line.strip()]
        with open(wordlists_dir / "familynames-usa-top1000.txt") as f:
            family_names = [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Wordlist file not found: {e}")

    # Use all names for maximum combinations
    # Combine first names (male + female = up to 2000 unique)
    first_names = list(set(female_names + male_names))
    # Use all family names (up to 1000)
    # This gives us up to 2000 x 1000 = 2M unique combinations
    # For patterns that only use firstname or lastname, we can generate up to 2000 or 1000 respectively

    emails = []
    domain = domain.strip().lower()

    # Generate emails based on pattern
    if pattern in ["firstname", "lastname"]:
        # For single-name patterns, we can use all names
        if pattern == "firstname":
            emails = [f"{name}@{domain}" for name in first_names[:max_emails]]
        else:  # lastname
            emails = [f"{name}@{domain}" for name in family_names[:max_emails]]
    else:
        # For combination patterns, generate all combinations up to max_emails
        for first_name in first_names:
            for family_name in family_names:
                if len(emails) >= max_emails:
                    break

                if pattern == "firstname.lastname":
                    email = f"{first_name}.{family_name}@{domain}"
                elif pattern == "firstnamelastname":
                    email = f"{first_name}{family_name}@{domain}"
                elif pattern == "firstname_lastname":
                    email = f"{first_name}_{family_name}@{domain}"
                elif pattern == "f.lastname":
                    email = f"{first_name[0]}.{family_name}@{domain}"
                elif pattern == "firstname.l":
                    email = f"{first_name}.{family_name[0]}@{domain}"
                elif pattern == "flastname":
                    email = f"{first_name[0]}{family_name}@{domain}"
                elif pattern == "firstinitial.lastname":
                    email = f"{first_name[0]}.{family_name}@{domain}"
                elif pattern == "firstname.lastinitial":
                    email = f"{first_name}.{family_name[0]}@{domain}"
                else:
                    # Default to firstname.lastname
                    email = f"{first_name}.{family_name}@{domain}"

                emails.append(email)

                if len(emails) >= max_emails:
                    break

            if len(emails) >= max_emails:
                break

    return {
        "emails": emails[:max_emails],
        "count": len(emails[:max_emails]),
        "pattern": pattern,
        "domain": domain,
    }


@app.get("/api/infrastructure")
async def get_infrastructure():
    """Get current AWS infrastructure resources."""
    global scanner, infrastructure_resources

    if scanner is None:
        return {
            "current_resources": [],
            "historical_resources": [],
            "total_resources": 0,
            "message": "No scanner initialized. AWS credentials required.",
        }

    # Query actual AWS resources to see what exists
    current_resources = []
    try:
        session = scanner.session

        # Check ECR Public repositories
        try:
            ecr_public = session.client("ecr-public")
            repos = ecr_public.describe_repositories()
            for repo in repos.get("repositories", []):
                if "quiet-riot-public-repo" in repo["repositoryName"]:
                    created_at = repo.get("createdAt")
                    current_resources.append(
                        {
                            "type": "ECR Public Repository",
                            "name": repo["repositoryName"],
                            "arn": repo.get("repositoryArn", ""),
                            "status": "active",
                            "created_at": (created_at.isoformat() if created_at else None),
                        }
                    )
        except Exception as e:
            logger.debug(f"Error checking ECR Public: {e}")

        # Check ECR Private repositories
        try:
            ecr_private = session.client("ecr")
            repos = ecr_private.describe_repositories()
            for repo in repos.get("repositories", []):
                if "quiet-riot-private-repo" in repo["repositoryName"]:
                    created_at = repo.get("createdAt")
                    current_resources.append(
                        {
                            "type": "ECR Private Repository",
                            "name": repo["repositoryName"],
                            "arn": repo.get("repositoryArn", ""),
                            "status": "active",
                            "created_at": (created_at.isoformat() if created_at else None),
                        }
                    )
        except Exception as e:
            logger.debug(f"Error checking ECR Private: {e}")

        # Check SNS topics
        try:
            sns = session.client("sns")
            topics = sns.list_topics()
            for topic in topics.get("Topics", []):
                if "quiet-riot-sns-topic" in topic["TopicArn"]:
                    current_resources.append(
                        {
                            "type": "SNS Topic",
                            "arn": topic["TopicArn"],
                            "status": "active",
                        }
                    )
        except Exception as e:
            logger.debug(f"Error checking SNS: {e}")

        # Check S3 buckets
        try:
            s3 = session.client("s3")
            buckets = s3.list_buckets()
            for bucket in buckets.get("Buckets", []):
                if "quiet-riot-bucket" in bucket["Name"]:
                    created_at = bucket.get("CreationDate")
                    current_resources.append(
                        {
                            "type": "S3 Bucket",
                            "name": bucket["Name"],
                            "status": "active",
                            "created_at": (created_at.isoformat() if created_at else None),
                        }
                    )
        except Exception as e:
            logger.debug(f"Error checking S3: {e}")

        # Get canonical ID from S3
        try:
            s3 = session.client("s3")
            buckets = s3.list_buckets()
            if buckets.get("Owner", {}).get("ID"):
                current_resources.append(
                    {
                        "type": "S3 Canonical ID",
                        "id": buckets["Owner"]["ID"],
                        "status": "active",
                    }
                )
        except Exception as e:
            logger.debug(f"Error getting canonical ID: {e}")

    except Exception as e:
        logger.error(f"Error querying AWS infrastructure: {e}")

    # Also include historical resources from completed scans
    historical_resources = []
    for scan_id, resources in infrastructure_resources.items():
        historical_resources.append(
            {
                "scan_id": scan_id,
                "scan_type": resources.get("scan_type"),
                "created_at": resources.get("created_at"),
                "resources": {
                    "ecr_public_repo": resources.get("ecr_public_repo"),
                    "ecr_private_repo": resources.get("ecr_private_repo"),
                    "sns_topic_arn": resources.get("sns_topic_arn"),
                    "s3_bucket": resources.get("s3_bucket"),
                    "canonical_id": resources.get("canonical_id"),
                },
            }
        )

    return {
        "current_resources": current_resources,
        "historical_resources": historical_resources,
        "total_resources": len(current_resources),
    }


@app.post("/api/infrastructure/cleanup")
async def cleanup_infrastructure():
    """Clean up all AWS infrastructure resources."""
    global scanner, infrastructure_resources

    if scanner is None:
        raise HTTPException(status_code=503, detail="No scanner initialized")

    try:
        # Clean up resources from the scanner's resource manager
        success = scanner.resource_mgr.cleanup_all(force=True)

        # Also clean up any orphaned resources by querying AWS directly
        session = scanner.session
        cleaned_count = 0

        # Clean up ECR Public repositories
        try:
            ecr_public = session.client("ecr-public")
            repos = ecr_public.describe_repositories()
            for repo in repos.get("repositories", []):
                if "quiet-riot-public-repo" in repo["repositoryName"]:
                    try:
                        ecr_public.delete_repository(repositoryName=repo["repositoryName"])
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Error deleting ECR Public repo {repo['repositoryName']}: {e}")
        except Exception as e:
            logger.debug(f"Error checking ECR Public: {e}")

        # Clean up ECR Private repositories
        try:
            ecr_private = session.client("ecr")
            repos = ecr_private.describe_repositories()
            for repo in repos.get("repositories", []):
                if "quiet-riot-private-repo" in repo["repositoryName"]:
                    try:
                        ecr_private.delete_repository(repositoryName=repo["repositoryName"])
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Error deleting ECR Private repo {repo['repositoryName']}: {e}")
        except Exception as e:
            logger.debug(f"Error checking ECR Private: {e}")

        # Clean up SNS topics
        try:
            sns = session.client("sns")
            topics = sns.list_topics()
            for topic in topics.get("Topics", []):
                if "quiet-riot-sns-topic" in topic["TopicArn"]:
                    try:
                        sns.delete_topic(TopicArn=topic["TopicArn"])
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Error deleting SNS topic {topic['TopicArn']}: {e}")
        except Exception as e:
            logger.debug(f"Error checking SNS: {e}")

        # Clean up S3 buckets
        try:
            s3 = session.client("s3")
            buckets = s3.list_buckets()
            for bucket in buckets.get("Buckets", []):
                if "quiet-riot-bucket" in bucket["Name"]:
                    try:
                        # Empty bucket first
                        bucket_name = bucket["Name"]
                        try:
                            objects = s3.list_objects_v2(Bucket=bucket_name)
                            if "Contents" in objects:
                                for obj in objects["Contents"]:
                                    s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
                        except Exception:
                            pass
                        s3.delete_bucket(Bucket=bucket_name)
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Error deleting S3 bucket {bucket['Name']}: {e}")
        except Exception as e:
            logger.debug(f"Error checking S3: {e}")

        # Clear infrastructure tracking
        infrastructure_resources.clear()

        if success and cleaned_count > 0:
            return {
                "status": "success",
                "message": f"All infrastructure resources cleaned up successfully ({cleaned_count} resources removed)",
                "resources_cleaned": cleaned_count,
            }
        elif success:
            return {
                "status": "success",
                "message": "All infrastructure resources cleaned up successfully",
            }
        else:
            return {
                "status": "partial",
                "message": f"Some resources may not have been cleaned up ({cleaned_count} resources removed)",
                "resources_cleaned": cleaned_count,
            }
    except Exception as e:
        logger.exception(f"Error cleaning up infrastructure: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "scanner_initialized": scanner is not None,
        "credentials_configured": not credentials_required,
    }


def main():
    """Main entry point for FastAPI server."""
    import uvicorn

    cfg = config.get_config()
    logger.info("Starting Quiet Riot FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=cfg.log_level.lower())  # nosec B104


if __name__ == "__main__":
    main()
