#!/usr/bin/env python3
"""
Configuration singleton for Quiet Riot.
Manages application settings, AWS session state, and logging configuration.
"""
import logging
import os
from pathlib import Path
import sys
from typing import List, Optional


class Config:
    """
    Singleton configuration class for Quiet Riot.

    Usage:
        config = Config.get_instance()
        config.init(session)
    """

    _instance: Optional["Config"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration if not already done."""
        if not self._initialized:
            self._reset()
            Config._initialized = True

    def _reset(self):
        """Reset configuration to defaults."""
        # AWS Configuration
        self.session: Optional[object] = None
        self.account_no: Optional[str] = None
        self.account_arn: Optional[str] = None

        # Scan Objects - resources created for enumeration
        self.scan_objects: List[str] = []

        # Logging Configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file: Optional[str] = os.getenv("LOG_FILE", None)
        self.log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.log_date_format: str = "%Y-%m-%d %H:%M:%S"

        # Application Configuration
        self.default_threads: int = int(os.getenv("QUIET_RIOT_DEFAULT_THREADS", "100"))
        self.default_profile: str = os.getenv("AWS_PROFILE", os.getenv("QUIET_RIOT_DEFAULT_PROFILE", "default"))
        self.default_region: str = os.getenv("AWS_REGION", "us-east-1")

        # Output Configuration
        self.results_dir: Path = Path("results")
        self.results_dir.mkdir(exist_ok=True)

        # Logging setup
        self._setup_logging()

    @classmethod
    def get_instance(cls) -> "Config":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def init(self, session) -> None:
        """
        Initialize configuration with AWS session.

        Args:
            session: Boto3 session object
        """
        self.session = session
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        self.account_no = identity["Account"]
        self.account_arn = identity["Arn"]
        self.scan_objects = []
        logging.info(f"Initialized config for AWS account: {self.account_no}")

    def add_scan_object(self, obj: str) -> None:
        """
        Add a scan object to the list.

        Args:
            obj: Object identifier (ARN, bucket name, etc.)
        """
        self.scan_objects.append(obj)

    def clear_scan_objects(self) -> None:
        """Clear all scan objects."""
        self.scan_objects.clear()

    def _setup_logging(self) -> None:
        """Configure logging for the application."""
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level, logging.INFO))

        # Clear existing handlers
        root_logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(self.log_format, datefmt=self.log_date_format)

        # Console handler (always add)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level, logging.INFO))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (if log file specified)
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)  # File gets all logs
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            logging.info(f"Logging to file: {self.log_file}")

        # Set levels for third-party libraries
        logging.getLogger("boto3").setLevel(logging.WARNING)
        logging.getLogger("botocore").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        logging.info(f"Logging configured at level: {self.log_level}")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a module.

        Args:
            name: Logger name (typically __name__)

        Returns:
            Logger instance
        """
        return logging.getLogger(name)

    def set_log_level(self, level: str) -> None:
        """
        Set the logging level.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = level.upper()
        logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))
        for handler in logging.getLogger().handlers:
            handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        logging.info(f"Log level changed to: {self.log_level}")

    def __repr__(self) -> str:
        """String representation of config."""
        return (
            f"Config(account_no={self.account_no}, "
            f"scan_objects={len(self.scan_objects)}, "
            f"log_level={self.log_level})"
        )


# Convenience function for backward compatibility
def get_config() -> Config:
    """Get the config singleton instance."""
    return Config.get_instance()
