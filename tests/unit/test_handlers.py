"""Unit tests for wordlist and result handlers."""

import pytest

from quiet_riot.core.result_handler import ResultHandler
from quiet_riot.core.wordlist_handler import WordlistHandler


def test_load_wordlist(tmp_path):
    wl = tmp_path / "words.txt"
    wl.write_text("alpha\n\nbeta\n  \ngamma\n")
    words = WordlistHandler().load_wordlist(str(wl))
    assert words == ["alpha", "beta", "gamma"]


def test_load_missing_wordlist_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        WordlistHandler().load_wordlist(str(tmp_path / "nope.txt"))


def test_save_and_reload_wordlist(tmp_path):
    out = tmp_path / "out.txt"
    WordlistHandler().save_wordlist(["a", "b"], str(out))
    assert out.read_text().splitlines() == ["a", "b"]


def test_result_roundtrip(tmp_path):
    handler = ResultHandler(results_dir=tmp_path)
    path = handler.save_results(["123456789012", "210987654321"], "1")
    assert path.exists()
    assert handler.load_results(path) == ["123456789012", "210987654321"]
