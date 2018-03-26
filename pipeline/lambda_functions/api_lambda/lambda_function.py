import boto3
import os
import json
import botocore.exceptions
import logging

logger = logging.getLogger(__name__)
sfn = boto3.client('stepfunctions')
sfn_name = os.environ['statemachine_name']


def get_arn(sfn_name):
    """
    Get arn of given statemachine
    :param sfn_name: statemachine name
    :return: arn
    """
    for ma in sfn.list_state_machines()['stateMachines']:
        if ma['name'].startswith(sfn_name):
            return ma['stateMachineArn']


SFN_ARN = get_arn(sfn_name)


def lambda_handler(event, context):
    """
    Lambda function to execute statemachine
    """
    try:
        sfn.start_execution(stateMachineArn=SFN_ARN, input=json.dumps(event))
    except botocore.exceptions.ClientError as e:
        raise e
    return 200
