import unittest
from click.testing import CliRunner
import shlex
from quiet_riot.command.enum import enum


class EnumClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_enum_help(self):
        """command.enum: should return exit code 0"""
        args = "--help"
        args = shlex.split(args)
        result = self.runner.invoke(enum, ["--help"])
        self.assertTrue(result.exit_code == 0)

