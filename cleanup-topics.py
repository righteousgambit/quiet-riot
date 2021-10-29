#!/usr/bin/env python3
import boto3
sns = boto3.client('sns')


sns_topics = sns.list_topics()
for i in range(0, len(sns_topics['Topics'])):
    if len(sns_topics['Topics']) != 0:
        if 'quiet-riot-sns-top' in sns_topics['Topics'][i]['TopicArn']:
            print('Found One!')
            print(sns_topics['Topics'][i]['TopicArn'])
            sns.delete_topic(TopicArn= sns_topics['Topics'][i]['TopicArn'])
        else:
            print("The checked ARN was not a Quiet Riot topic.")

