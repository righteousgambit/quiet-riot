# import unittest
# from quiet_riot.enumeration.thread_manager import ThreadManager
#
#
# class ThreadManagerUnitTests(unittest.TestCase):
#     def setUp(self):
#         self.runner = CliRunner()
#
#     def test_enum_help(self):
#         """command.enum: should return exit code 0"""
#         args = "--help"
#         args = shlex.split(args)
#         result = self.runner.invoke(enum, ["--help"])
#         self.assertTrue(result.exit_code == 0)
#
