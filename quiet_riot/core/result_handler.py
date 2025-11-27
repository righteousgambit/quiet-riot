"""
Result handling for Quiet Riot.
"""
from datetime import datetime
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class ResultHandler:
    """Handles scan result operations."""

    def __init__(self, results_dir: Optional[Path] = None):
        """
        Initialize result handler.

        Args:
            results_dir: Directory for results (default: results/)
        """
        if results_dir is None:
            results_dir = Path("results")
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

    def save_results(self, valid_principals: List[str], scan_type: str) -> Path:
        """
        Save scan results to file.

        Args:
            valid_principals: List of valid principals found
            scan_type: Type of scan performed

        Returns:
            Path to results file
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"valid_scan_results-{scan_type}-{timestamp}.txt"
        filepath = self.results_dir / filename

        logger.info(f"Saving {len(valid_principals)} results to {filepath}")
        with open(filepath, "w") as f:
            for principal in valid_principals:
                f.write(f"{principal}\n")

        return filepath

    def load_results(self, results_file: Path) -> List[str]:
        """
        Load results from file.

        Args:
            results_file: Path to results file

        Returns:
            List of principals from results file
        """
        logger.info(f"Loading results from {results_file}")
        with open(results_file) as f:
            principals = [line.strip() for line in f if line.strip()]
        return principals
