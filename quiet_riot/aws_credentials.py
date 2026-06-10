#!/usr/bin/env python3
"""
AWS Credentials Management Module.

Handles AWS credential configuration, ARN parsing, profile creation,
and SSO profile setup.
"""

import configparser
import logging
from pathlib import Path
import re

import boto3
from botocore.exceptions import ClientError, ProfileNotFound

logger = logging.getLogger(__name__)


class ARNParseError(Exception):
    """Exception raised when ARN parsing fails."""

    pass


class ProfileCreationError(Exception):
    """Exception raised when profile creation fails."""

    pass


class AWSCredentialsManager:
    """Manages AWS credentials, profiles, and ARN handling."""

    def __init__(self):
        """Initialize the credentials manager."""
        self.aws_config_path = Path.home() / ".aws" / "config"
        self.aws_credentials_path = Path.home() / ".aws" / "credentials"
        self._ensure_aws_dir()

    def _ensure_aws_dir(self):
        """Ensure AWS directory exists."""
        self.aws_config_path.parent.mkdir(parents=True, exist_ok=True)
        self.aws_credentials_path.parent.mkdir(parents=True, exist_ok=True)

    def parse_arn(self, arn: str) -> dict[str, str]:
        """
        Parse an AWS ARN into its components.

        Args:
            arn: Full ARN string (e.g., arn:aws:iam::123456789012:role/MyRole)

        Returns:
            Dictionary with keys: partition, service, region, account_id, resource_type, resource_name

        Raises:
            ARNParseError: If ARN format is invalid
        """
        # ARN format: arn:partition:service:region:account-id:resource-type/resource-name
        arn_pattern = r"^arn:([^:]+):([^:]+):([^:]*):([^:]*):([^:/]+)(?:/(.+))?$"
        match = re.match(arn_pattern, arn)

        if not match:
            raise ARNParseError(f"Invalid ARN format: {arn}")

        partition, service, region, account_id, resource_type, resource_name = match.groups()

        return {
            "partition": partition,
            "service": service,
            "region": region or "",
            "account_id": account_id or "",
            "resource_type": resource_type,
            "resource_name": resource_name or "",
            "full_arn": arn,
        }

    def is_arn(self, value: str) -> bool:
        """
        Check if a string is a valid ARN.

        Args:
            value: String to check

        Returns:
            True if value is an ARN, False otherwise
        """
        try:
            self.parse_arn(value)
            return True
        except ARNParseError:
            return False

    def profile_exists(self, profile_name: str) -> bool:
        """
        Check if an AWS profile exists.

        Args:
            profile_name: Profile name to check

        Returns:
            True if profile exists, False otherwise
        """
        try:
            config = configparser.ConfigParser()
            config.read(self.aws_config_path)

            # Check in config file (for SSO profiles)
            if config.has_section(f"profile {profile_name}"):
                return True

            # Check in credentials file (for access key profiles)
            creds = configparser.ConfigParser()
            creds.read(self.aws_credentials_path)
            if creds.has_section(profile_name):
                return True

            # Check if default profile (no section needed)
            return profile_name == "default"
        except Exception as e:
            logger.debug(f"Error checking profile existence: {e}")
            return False

    def get_profile_arn(self, profile_name: str) -> str | None:
        """
        Get the ARN associated with a profile by checking the current identity.

        Args:
            profile_name: Profile name

        Returns:
            ARN string if available, None otherwise
        """
        try:
            session = boto3.Session(profile_name=profile_name)
            sts = session.client("sts")
            identity = sts.get_caller_identity()
            arn = identity.get("Arn")
            return str(arn) if arn else None
        except Exception as e:
            logger.debug(f"Could not get ARN for profile {profile_name}: {e}")
            return None

    def create_sso_profile(
        self,
        profile_name: str,
        sso_start_url: str,
        sso_region: str,
        sso_account_id: str,
        sso_role_name: str,
        region: str = "us-east-1",
    ) -> bool:
        """
        Create an AWS SSO profile in the config file.

        Args:
            profile_name: Name for the profile
            sso_start_url: SSO start URL
            sso_region: SSO region
            sso_account_id: SSO account ID
            sso_role_name: SSO role name
            region: Default region for the profile

        Returns:
            True if successful, False otherwise

        Raises:
            ProfileCreationError: If profile creation fails
        """
        try:
            config = configparser.ConfigParser()
            config.read(self.aws_config_path)

            section_name = f"profile {profile_name}" if profile_name != "default" else "default"

            if not config.has_section(section_name):
                config.add_section(section_name)

            config.set(section_name, "sso_start_url", sso_start_url)
            config.set(section_name, "sso_region", sso_region)
            config.set(section_name, "sso_account_id", sso_account_id)
            config.set(section_name, "sso_role_name", sso_role_name)
            config.set(section_name, "region", region)
            config.set(section_name, "output", "json")

            with open(self.aws_config_path, "w") as f:
                config.write(f)

            logger.info(f"Created SSO profile: {profile_name}")
            return True
        except Exception as e:
            raise ProfileCreationError(f"Failed to create SSO profile: {e}") from e

    def create_assume_role_profile(
        self,
        profile_name: str,
        role_arn: str,
        source_profile: str = "default",
        region: str = "us-east-1",
        external_id: str | None = None,
    ) -> bool:
        """
        Create an AWS profile that assumes a role.

        Args:
            profile_name: Name for the profile
            role_arn: ARN of the role to assume
            source_profile: Source profile to use for assuming the role
            region: Default region for the profile
            external_id: Optional external ID for role assumption

        Returns:
            True if successful, False otherwise

        Raises:
            ProfileCreationError: If profile creation fails
        """
        try:
            config = configparser.ConfigParser()
            config.read(self.aws_config_path)

            section_name = f"profile {profile_name}" if profile_name != "default" else "default"

            if not config.has_section(section_name):
                config.add_section(section_name)

            config.set(section_name, "role_arn", role_arn)
            config.set(section_name, "source_profile", source_profile)
            config.set(section_name, "region", region)
            config.set(section_name, "output", "json")

            if external_id:
                config.set(section_name, "external_id", external_id)

            with open(self.aws_config_path, "w") as f:
                config.write(f)

            logger.info(f"Created assume role profile: {profile_name} (role: {role_arn})")
            return True
        except Exception as e:
            raise ProfileCreationError(f"Failed to create assume role profile: {e}") from e

    def create_profile_from_arn(
        self,
        arn: str,
        profile_name: str | None = None,
        prefer_sso: bool = True,
    ) -> str:
        """
        Create an AWS profile from an ARN.

        This function attempts to:
        1. Parse the ARN
        2. If it's an IAM role, create a profile that assumes that role
        3. If prefer_sso is True, try to detect SSO configuration

        Args:
            arn: Full ARN string
            profile_name: Optional profile name (auto-generated if not provided)
            prefer_sso: Whether to prefer SSO configuration

        Returns:
            Profile name that was created or used

        Raises:
            ARNParseError: If ARN format is invalid
            ProfileCreationError: If profile creation fails
        """
        arn_info = self.parse_arn(arn)

        # Generate profile name if not provided
        if not profile_name:
            # Use role name or generate from account and resource
            if arn_info["resource_name"]:
                profile_name = f"qr-{arn_info['account_id']}-{arn_info['resource_name']}"
            else:
                profile_name = f"qr-{arn_info['account_id']}-{arn_info['resource_type']}"
            # Sanitize profile name
            profile_name = re.sub(r"[^a-zA-Z0-9_-]", "-", profile_name)
            profile_name = profile_name[:64]  # AWS profile name limit

        # Check if profile already exists
        if self.profile_exists(profile_name):
            logger.info(f"Profile {profile_name} already exists, using it")
            return profile_name

        # Handle IAM role ARNs
        if arn_info["service"] == "iam" and arn_info["resource_type"] == "role":
            # Try to create assume role profile
            # We need a source profile - try default first
            source_profile = "default"
            if not self.profile_exists(source_profile):
                # Try to find any existing profile
                config = configparser.ConfigParser()
                config.read(self.aws_config_path)
                sections = [s.replace("profile ", "") for s in config.sections() if s.startswith("profile ")]
                if sections:
                    source_profile = sections[0]
                else:
                    raise ProfileCreationError(
                        "No source profile available for role assumption. Please configure a base AWS profile first."
                    )

            self.create_assume_role_profile(
                profile_name=profile_name,
                role_arn=arn,
                source_profile=source_profile,
            )
            return profile_name

        # For other ARN types, we can't automatically create profiles
        raise ProfileCreationError(
            f"Cannot automatically create profile for ARN type: {arn_info['service']}/{arn_info['resource_type']}. "
            "Please create the profile manually or use an IAM role ARN."
        )

    def validate_session(
        self, session: boto3.Session | None = None, profile_name: str | None = None
    ) -> tuple[bool, str | None]:
        """
        Validate that an AWS session has valid credentials.

        Args:
            session: Optional boto3 session to validate
            profile_name: Optional profile name to create session from

        Returns:
            Tuple of (is_valid, arn_or_error_message)
        """
        try:
            if session is None:
                if profile_name:
                    session = boto3.Session(profile_name=profile_name)
                else:
                    session = boto3.Session()

            sts = session.client("sts")
            identity = sts.get_caller_identity()
            arn = identity.get("Arn")
            return True, arn
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            return False, f"AWS API error: {error_code}"
        except ProfileNotFound:
            return False, f"Profile not found: {profile_name}"
        except Exception as e:
            return False, f"Failed to validate credentials: {str(e)}"

    def get_or_create_session(
        self,
        profile_or_arn: str,
        prefer_profile: bool = True,
    ) -> tuple[boto3.Session, str]:
        """
        Get or create an AWS session from a profile name or ARN.

        Args:
            profile_or_arn: Profile name or ARN string
            prefer_profile: If True, treat as profile name first, then ARN

        Returns:
            Tuple of (boto3.Session, profile_name_used)

        Raises:
            ARNParseError: If ARN format is invalid
            ProfileCreationError: If profile creation fails
            ValueError: If credentials are invalid
        """
        # If prefer_profile is True, check if it's a profile name first
        if prefer_profile and not self.is_arn(profile_or_arn):
            # Treat as profile name
            if self.profile_exists(profile_or_arn):
                session = boto3.Session(profile_name=profile_or_arn)
                is_valid, error = self.validate_session(session)
                if is_valid:
                    return session, profile_or_arn
                else:
                    raise ValueError(f"Profile {profile_or_arn} exists but credentials are invalid: {error}")

        # Check if it's an ARN
        if self.is_arn(profile_or_arn):
            # Create profile from ARN
            profile_name = self.create_profile_from_arn(profile_or_arn)
            session = boto3.Session(profile_name=profile_name)
            is_valid, error = self.validate_session(session)
            if is_valid:
                return session, profile_name
            else:
                raise ValueError(f"Created profile from ARN but credentials are invalid: {error}")

        # Try as profile name (even if prefer_profile is False)
        if self.profile_exists(profile_or_arn):
            session = boto3.Session(profile_name=profile_or_arn)
            is_valid, error = self.validate_session(session)
            if is_valid:
                return session, profile_or_arn
            else:
                raise ValueError(f"Profile {profile_or_arn} exists but credentials are invalid: {error}")

        # If we get here, it's neither a valid profile nor an ARN
        raise ValueError(
            f"'{profile_or_arn}' is neither a valid profile name nor a valid ARN. "
            "Please provide a profile name or an IAM role ARN."
        )


# Global instance
_credentials_manager: AWSCredentialsManager | None = None


def get_credentials_manager() -> AWSCredentialsManager:
    """Get the global credentials manager instance."""
    global _credentials_manager
    if _credentials_manager is None:
        _credentials_manager = AWSCredentialsManager()
    return _credentials_manager
