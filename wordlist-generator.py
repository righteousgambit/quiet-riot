#!/usr/bin/env python3

known_accounts_file = 'wordlists/known_valid_account_ids.txt'
servicerole_file = 'wordlists/service-roles.txt'
wordlist = 'scan-list.txt'

new_list = []
account_list = []

with open(known_accounts_file) as f:
    account_list = [x.rstrip() for x in f]

with open(servicerole_file) as file:
    my_list = [x.rstrip() for x in file]   
    for item in my_list:
        for i in account_list:
            new_list.append('arn:aws:iam::'+i+':role/'+item)
    with open(wordlist, 'a+') as f:
        for item in new_list:
            f.write("%s\n" % item)