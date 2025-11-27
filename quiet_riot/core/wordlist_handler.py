"""
Wordlist handling for Quiet Riot.
"""
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class WordlistHandler:
    """Handles wordlist operations."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize wordlist handler.

        Args:
            base_path: Base path for wordlists (default: package wordlists directory)
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent / "wordlists"
        self.base_path = base_path

    def load_wordlist(self, wordlist_path: str) -> List[str]:
        """
        Load wordlist from file.

        Args:
            wordlist_path: Path to wordlist file

        Returns:
            List of words from wordlist
        """
        path = Path(wordlist_path)
        if not path.is_absolute():
            path = self.base_path / path

        if not path.exists():
            raise FileNotFoundError(f"Wordlist file not found: {path}")

        logger.info(f"Loading wordlist from {path}")
        with open(path) as f:
            words = [line.strip() for line in f if line.strip()]

        logger.info(f"Loaded {len(words)} words from wordlist")
        return words

    def save_wordlist(self, words: List[str], output_path: str) -> Path:
        """
        Save wordlist to file.

        Args:
            words: List of words to save
            output_path: Output file path

        Returns:
            Path to saved file
        """
        path = Path(output_path)
        logger.info(f"Saving {len(words)} words to {path}")
        with open(path, "w") as f:
            for word in words:
                f.write(f"{word}\n")
        return path
