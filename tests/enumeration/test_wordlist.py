import unittest
import os
import json
from quiet_riot.enumeration.wordlist import get_rendered_wordlist


class WordlistUnitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.wordlist_file = os.path.join(os.path.dirname(__file__), "example-wordlist.txt")
        self.wordlist = get_rendered_wordlist(wordlist_principal_type="role", target_account_number="111122223333",
                                              wordlist_file=self.wordlist_file)

    def test_get_rendered_wordlist(self):
        results = self.wordlist
        expected_results = [
            "arn:aws:iam::111122223333:role/aws-service-role/access-analyzer.amazonaws.com/AWSServiceRoleForAccessAnalyzer",
            "arn:aws:iam::111122223333:role/aws-service-role/accountdiscovery.ssm.amazonaws.com/AWSServiceRoleForAmazonSSM_AccountDiscovery",
            "arn:aws:iam::111122223333:role/aws-service-role/acm.amazonaws.com/AWSServiceRoleForCertificateManager",
            "arn:aws:iam::111122223333:role/aws-service-role/appmesh.amazonaws.com/AWSServiceRoleForAppMesh",
            "arn:aws:iam::111122223333:role/aws-service-role/apprunner.amazonaws.com/AWSServiceRoleForAppRunner"
        ]
        for expected in expected_results:
            self.assertTrue(expected in results)
        print(json.dumps(results, indent=4))
        # self.assertListEqual(results, expected_results)

    def test_get_chunked_wordlist(self):
        thread_count = 700
        list_size = int(len(self.wordlist) / int(thread_count))
        if list_size >= 1:
            # list_size
            pass
        else:
            list_size = 1

        def get_chunked_wordlist(wordlist):
            # Based on the number of desired threads and the overall # of words in the wordlist provided, chunk the wordlist into smaller wordlists and then make a list of lists that can be passed in threader to services
            chunks = [wordlist[x:x + list_size] for x in range(0, len(wordlist), list_size)]
            new_list = []
            for list in chunks:
                new_list.append(list)
            print('Scanning Started with Quiet Riot')
            return new_list

        results = get_chunked_wordlist(self.wordlist)
        print(json.dumps(results, indent=4))
        expected_results = [
            [
                "arn:aws:iam::111122223333:role/aws-service-role/access-analyzer.amazonaws.com/AWSServiceRoleForAccessAnalyzer"
            ],
            [
                "arn:aws:iam::111122223333:role/aws-service-role/accountdiscovery.ssm.amazonaws.com/AWSServiceRoleForAmazonSSM_AccountDiscovery"
            ],
            [
                "arn:aws:iam::111122223333:role/aws-service-role/acm.amazonaws.com/AWSServiceRoleForCertificateManager"
            ],
            [
                "arn:aws:iam::111122223333:role/aws-service-role/appmesh.amazonaws.com/AWSServiceRoleForAppMesh"
            ],
            [
                "arn:aws:iam::111122223333:role/aws-service-role/apprunner.amazonaws.com/AWSServiceRoleForAppRunner"
            ]
        ]
        flat_expected_results = [item for sublist in expected_results for item in sublist]
        flat_results = [item for sublist in results for item in sublist]
        for expected in flat_expected_results:
            self.assertTrue(expected in flat_results)
        # self.assertListEqual(results, expected_results)
