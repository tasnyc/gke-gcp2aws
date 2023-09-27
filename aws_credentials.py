#!/usr/bin/env python3
import requests
import boto3
import json
import sys


'''
This script accepts one argument for the AWS role ARN
'''

def get_token():
    url = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?format=standard&audience=gcp'
    headers = {'Metadata-Flavor': 'Google'}
    try:
        req = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
        exit(0)

    if req.ok:
        return req.text
    else:
        raise SystemExit('GCE metadata error')
        exit(0)

if __name__ == '__main__':
    try:
        role_arn = sys.argv[1]
    except IndexError:
        print("Please specify an argument for AWS role ARN")
        exit(0)

    token = get_token()
    account_id = role_arn.split(':')[4]
    role_name = role_arn.split('/')[1]
    session_name = '{}.{}'.format(account_id, role_name)

    sts = boto3.client('sts', aws_access_key_id='', aws_secret_access_key='')
    res = sts.assume_role_with_web_identity(
        RoleArn=role_arn,
        WebIdentityToken=token,
        RoleSessionName=session_name)

    credentials = {
        'Version': 1,
        'AccessKeyId': res['Credentials']['AccessKeyId'],
        'SecretAccessKey': res['Credentials']['SecretAccessKey'],
        'SessionToken': res['Credentials']['SessionToken'],
        'Expiration': res['Credentials']['Expiration'].isoformat()
    }

    print(json.dumps(credentials))
