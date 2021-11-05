#!/usr/bin/env python3

wordlist_file = 'wordlists/service-linked-roles.txt'
account_no = 'wordlists/known_valid_account_ids.txt'
new_list = []
output_list = 'complete-footprint.txt'

with open(account_no) as f:
    account_list = [x.rstrip() for x in f]

with open(wordlist_file) as file:
    my_list = [x.rstrip() for x in file]
    for account_no in account_list:   
        for item in my_list:
            new_list.append('arn:aws:iam::'+account_no+':'+item)


with open(output_list, 'a+') as f:
    for item in new_list:
        f.write("%s\n" % item)