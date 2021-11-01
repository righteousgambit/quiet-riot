#!/usr/bin/env python3


wordlist_type = input('Provide your wordlist type: ')
wordlist = 'test.txt'

account_no = '201012399609'
new_list = []

with open('wordlists/service-linked-roles.txt') as file:
    my_list = [x.rstrip() for x in file]   
    if wordlist_type == 'footprint':
        for item in my_list:
            new_list.append('arn:aws:iam::'+account_no+':role/'+item)
        with open(wordlist, 'a+') as f:
            for item in new_list:
                f.write("%s\n" % item)