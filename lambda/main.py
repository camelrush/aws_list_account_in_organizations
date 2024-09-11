import os
import boto3
from boto3.session import Session

PAYMENT_ACCOUNT_ID = os.environ['PAYMENT_ACCOUNT_ID']
ASSUME_ROLE_NAME = os.environ['ASSUME_ROLE_NAME']

def handler(event, context):
    
    # 取得したいOUのIDを指定
    root_ou_id = event['ou-id']
     
    # PaymentAccountにAssumeRole
    assume_role_arn = f'arn:aws:iam::{PAYMENT_ACCOUNT_ID}:role/{ASSUME_ROLE_NAME}'
    assume_session = assume_role(assume_role_arn, 'list_account_session')

    # AWS Organizationsクライアントの作成
    organizations = assume_session.client('organizations')
    
    # OU配下の全アカウントを再帰的に取得
    accounts = list_accounts_for_ou(organizations, root_ou_id)
    
    # 結果を出力
    for account in accounts:
        #print(f"Account ID: {account['Id']}, Account Name: {account['Name']}")
        print(f"Account ID: {account['Id']}, Account Name: {account['Name']}, account_info: {account}")


# 指定されたOU配下の全てのアカウントを再帰的に取得する関数
def list_accounts_for_ou(organizations, ou_id):
    accounts = []
    
    # 指定されたOU配下のアカウントを取得
    response = organizations.list_accounts_for_parent(ParentId=ou_id)
    accounts.extend(response['Accounts'])
    
    # 指定されたOU配下のサブOUを取得
    response = organizations.list_organizational_units_for_parent(ParentId=ou_id)
    ous = response['OrganizationalUnits']
    
    # サブOUに対して再帰的にアカウントを取得
    for ou in ous:
        accounts.extend(list_accounts_for_ou(organizations, ou['Id']))
    
    return accounts


def assume_role(role_arn, session_name):

    sts_connection = boto3.client('sts')
    acct_b = sts_connection.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )
    session = Session(
        aws_access_key_id=acct_b['Credentials']['AccessKeyId'],
        aws_secret_access_key=acct_b['Credentials']['SecretAccessKey'],
        aws_session_token=acct_b['Credentials']['SessionToken']
    )
    return session