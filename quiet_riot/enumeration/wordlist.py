from quiet_riot.shared.constants import SERVICE_LINKED_ROLES_FILE
from quiet_riot.shared.utils import read_file_by_lines, read_file


def get_rendered_wordlist(wordlist_principal_type: str, target_account_number: str, wordlist_file: str = SERVICE_LINKED_ROLES_FILE):
    if wordlist_principal_type not in ["user", "role"]:
        raise Exception("Invalid wordlist_principal_type")  # TODO: Figure out a better way of managing this
    initial_wordlist = read_file_by_lines(wordlist_file)
    wordlist = set()  # Store the new wordlist
    for item in initial_wordlist:
        wordlist.add(f"arn:aws:iam::{target_account_number}:{wordlist_principal_type}/{item}")
    wordlist = list(wordlist)
    wordlist.sort()
    return wordlist
