#!/usr/bin/env python3
import boto3

sts = boto3.client('sts')

def init():
    global scan_objects
    scan_objects = []
    global account_no
    account_no = sts.get_caller_identity()['Account']