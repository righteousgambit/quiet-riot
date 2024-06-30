#!/usr/bin/env python3
import boto3
import json

session = boto3.Session(profile_name='default')
client = session.client('iam')


def iam_assume_role_princ_checker(rand_account_id):
  policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Federated": rand_account_id
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
  try:
    policy_blob = json.dumps(policy)
    response = client.update_assume_role_policy(
    RoleName='aqua-test-role',
    PolicyDocument=policy_blob
  )
    print(rand_account_id)
  except BaseException as err:
    print(err)
    pass

#iam_assume_role_princ_checker(rand_account_id)

with open('complete-footprint.txt') as f:
    my_list = [x.rstrip() for x in f]
    for i in my_list:
        iam_assume_role_princ_checker(i)