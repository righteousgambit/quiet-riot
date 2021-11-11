import unittest
from click.testing import CliRunner
import shlex
from quiet_riot.command.global_enum import global_enum


class GlobalEnumClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_global_enum_help(self):
        """command.global_enum: should return exit code 0"""
        args = "--help"
        args = shlex.split(args)
        result = self.runner.invoke(global_enum, ["--help"])
        self.assertTrue(result.exit_code == 0)

