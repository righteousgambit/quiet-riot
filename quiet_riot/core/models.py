"""
Data models for Quiet Riot.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ScanType(str, Enum):
    """Enumeration of supported scan types."""

    AWS_ACCOUNT_IDS = "1"
    MICROSOFT_365_DOMAINS = "2"
    AWS_SERVICES_FOOTPRINTING = "3"
    AWS_ROOT_USER_EMAIL = "4"
    AWS_IAM_PRINCIPALS = "5"
    MICROSOFT_365_USERS = "6"
    GOOGLE_WORKSPACE_USERS = "7"
    AWS_IAM_ROLES = "5.1"
    AWS_IAM_USERS = "5.2"


@dataclass
class ScanConfig:
    """Configuration for a scan operation."""

    scan_type: ScanType
    threads: int = 100
    wordlist_path: Optional[str] = None
    aws_profile: str = "default"
    account_id: Optional[str] = None
    domain_name: Optional[str] = None
    email_option: Optional[str] = None
    email_list_path: Optional[str] = None
    single_email: Optional[str] = None
    timeout: Optional[int] = None
    log_level: Optional[str] = None
    cleanup: bool = True


@dataclass
class ScanResult:
    """Results from a scan operation."""

    scan_id: str
    scan_type: ScanType
    status: str  # "running", "completed", "failed"
    valid_principals: List[str]
    total_scanned: int
    start_time: datetime
    end_time: Optional[datetime] = None
    results_file: Optional[str] = None
    error: Optional[str] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_scanned == 0:
            return 0.0
        return (len(self.valid_principals) / self.total_scanned) * 100

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate scan duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
