#!/usr/bin/env python3
import boto3

def init(session):
    sts = session.client('sts')
    global scan_objects
    scan_objects = []
    global account_no
    account_no = sts.get_caller_identity()['Account']
