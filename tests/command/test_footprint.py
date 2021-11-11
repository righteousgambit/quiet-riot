import unittest
from click.testing import CliRunner
import shlex
from quiet_riot.command.footprint import footprint


class FootprintClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_footprint_help(self):
        """command.footprint: should return exit code 0"""
        args = "--help"
        args = shlex.split(args)
        result = self.runner.invoke(footprint, ["--help"])
        self.assertTrue(result.exit_code == 0)

