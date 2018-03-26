""" Creates lambda function given parameters"""

import boto3
import logging
import botocore.exceptions
from awacs.aws import Allow, Policy, Principal, Statement
from awacs.sts import AssumeRole
from troposphere import Template, Ref, iam, GetAtt, awslambda, Output, Export, Sub
from cfn_stack_builder.utils import build, delete

logger = logging.getLogger(__name__)
cfn = boto3.client('cloudformation')


class LambdaTemplate:
    def __init__(self, *, fct_name, stage, s3_bucket, policies, env_vars={},
                 timeout=30, memory=128):
        """
        Lambda function template
        :param stage: (str) development stage
        :param fct_name: (str) name of the lambda function
        :param s3_bucket: (str) s3 bucket name containing zipped lambda
        :param policies: (list(iam.policies)) needed iam policies
        :param env_vars: (dict) dictionary with environment variables
        :param timeout: (int) timeout in sec
        :param memory: (int) memory size
        """
        self.template = Template()
        self.stack_name = f'{fct_name}Stack-{stage}'
        self.fct_name = fct_name
        self.s3_bucket = s3_bucket
        self.policies = policies
        self.env_vars = env_vars
        self.timeout = timeout
        self.memory = memory
        self.function = None
        self.execution_role = None
        self.output = None

    def create_stack(self):
        """
        Generate template components and create template resources
        """
        self.add_execution_role(). \
            add_lambda_resource(). \
            add_outputs()
        build(stack_name=self.stack_name,
              template=self.template)
        return self.template

    def delete_stack(self):
        """
        Delete stack resources
        """
        delete(stack_name=self.stack_name)

    def add_execution_role(self):
        """ 
        Defines execution role for lambda function
        """
        execution_role = self.template.add_resource(
            iam.Role(
                f'{self.fct_name}ExecutionRole',
                Path="/",
                Policies=self.policies,
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["lambda.amazonaws.com"]),
                        )
                    ]
                ),
            )
        )
        self.execution_role = execution_role
        return self

    def add_lambda_resource(self):
        """
        Definition of lambda properties
        """
        function = self.template.add_resource(
            awslambda.Function(
                f'{self.fct_name}Function',
                FunctionName=self.fct_name,
                Handler='lambda_function.lambda_handler',
                Role=GetAtt(self.execution_role, 'Arn'),
                Code=awslambda.Code(
                    S3Bucket=self.s3_bucket,
                    S3Key=f'{self.fct_name}.zip'
                ),
                Runtime='python3.6',
                Timeout=self.timeout,
                MemorySize=self.memory,
                Environment=awslambda.Environment('LambdaVars', Variables=self.env_vars)
            )
        )
        self.function = function
        return self

    def add_outputs(self):
        """
        Adds additional output variables
        """
        self.template.add_output(
            Output(
                f'{self.fct_name}ExecutionRoleOutput',
                Description=f'Execution Role of {self.fct_name}',
                Value=Ref(self.execution_role)
            )
        )
        return self
