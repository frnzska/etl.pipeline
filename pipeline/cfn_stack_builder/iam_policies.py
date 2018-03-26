"""
IAM policies for pipeline resources. Should be more restrictive in production, e.g. s3_access_policy should name the
concrete buckets where to read from and to write to
"""

from awacs.aws import Allow, Statement, Action, Policy
from troposphere import iam

logging_policy = iam.Policy(
    PolicyName='GrantLogs',
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [
            Statement(
                Sid='Logs',
                Effect=Allow,
                Action=[
                    Action('logs', 'CreateLogGroup'),
                    Action('logs', 'CreateLogStream'),
                    Action('logs', 'PutLogEvents')
                ],
                Resource=["arn:aws:logs:*:*:*"]
            ),
        ]
    }
)

invoke_state_machine_policy = iam.Policy(
    PolicyName='InvokeSates',
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [
            Statement(
                Sid='invokeStates',
                Effect=Allow,
                Action=[
                    Action('states', 'Describe*'),
                    Action('states', 'Get*'),
                    Action('states', 'List*'),
                    Action('states', 'Create*'),
                    Action('states', 'StartExecution'),
                    Action('states', 'Send*'),

                ],
                Resource=['arn:aws:states:*:*:*']
            ),
        ]
    }
)

s3_access_policy = iam.Policy(
    PolicyName='S3ReadAndWriteAccessPolicy',
    PolicyDocument=Policy(
        Statement=[
            Statement(
                Sid='S3Read',
                Effect=Allow,
                Action=[
                    Action('s3', 'List*'),
                    Action('s3', 'Get*'),
                    Action('s3', 'Put*'),
                ],
                Resource=['arn:aws:s3:::*']
            )
        ]
    )
)

invoke_lambda_policy = iam.Policy(
    PolicyName='InvokeLambda',
    PolicyDocument={
        "Version": "2012-10-17",
        "Statement": [
            Statement(
                Sid='invokeLambda',
                Effect=Allow,
                Action=[
                    Action('lambda', '*'),
                ],
                Resource=['*']
            ),
        ]
    }
)
