import unittest
from click.testing import CliRunner
import shlex
from quiet_riot.command.infra import create, destroy


class InfraCreateClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_infra_create_help(self):
        """command.infra.create: should return exit code 0"""
        args = "--help"
        args = shlex.split(args)
        result = self.runner.invoke(create, ["--help"])
        self.assertTrue(result.exit_code == 0)


class InfraDestroyClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_infra_create_help(self):
        """command.infra.destroy: should return exit code 0"""
        args = "--help"
        args = shlex.split(args)
        result = self.runner.invoke(destroy, ["--help"])
        self.assertTrue(result.exit_code == 0)
