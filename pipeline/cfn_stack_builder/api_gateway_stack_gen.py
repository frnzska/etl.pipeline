"""
Creates Api gateway resource and triggered lambda function
"""

from awacs.aws import Allow, Policy, Principal, Statement
from awacs.sts import AssumeRole
from troposphere import Template, Ref, iam, GetAtt, awslambda, Output, Sub, Join
from troposphere.apigateway import (RestApi, Method, Integration, IntegrationResponse,
                                    Resource, MethodResponse)
from cfn_stack_builder.utils import build, delete


class ApiGatewayTemplate:
    def __init__(self, *, name, stage, fct_name, s3_bucket, policies, env_vars={},
                 timeout=30, memory=128):
        """
        ApiGateway Template with triggered lambda function
        :param name: (str) rest api name
        :param stage: (str) stage of development of the stack
        :param fct_name: (str) name of triggered lambda
        :param s3_bucket: (str) name of s3_bucket with zipped lambda
        :param policies: (list(iam.policies)) needed iam policies
        :param env_vars: (dict) dictionary with environment variables
        :param timeout: (int) timeout in sec
        :param memory: (int) memory size
        """
        self.template = Template()
        self.stack_name = f'{name}Stack-{stage}'
        self.name = name
        self.fct_name = fct_name
        self.s3_bucket = s3_bucket
        self.policies = policies
        self.env_vars = env_vars
        self.timeout = timeout
        self.memory = memory
        self.rest_api = None
        self.resource = None
        self.execution_role = None
        self.function = None

    def add_execution_role(self):
        """ 
        Defines execution role for lambda function and adds to template
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
                            Principal=Principal("Service", ["lambda.amazonaws.com",
                                                            "apigateway.amazonaws.com"]),
                        )
                    ]
                ),
            )
        )
        self.execution_role = execution_role
        return self

    def create_stack(self):
        """
        Generate template components and create template resources
        """
        self.add_execution_role(). \
            add_lambda_resource(). \
            add_rest_api(). \
            add_resource(). \
            add_method()

        build(stack_name=self.stack_name, template=self.template)

    def delete_stack(self):
        """
        Delete stack resources
        """
        delete(stack_name=self.stack_name)

    def add_lambda_resource(self):
        """
        Adds definition of lambda properties to template
        """
        function = self.template.add_resource(
            awslambda.Function(
                f'{self.fct_name}',
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

    def add_rest_api(self):
        """
        Adds rest api to template 
        """
        self.rest_api = self.template.add_resource(RestApi(
            f'{self.name}',
            Name=f'{self.name}'
        ))
        return self

    def add_resource(self):
        """
        Adds api resource to template
        """
        self.resource = self.template.add_resource(Resource(
            f'{self.name}Resource',
            RestApiId=Ref(self.rest_api),
            PathPart='path',
            ParentId=GetAtt(self.rest_api, 'RootResourceId'),
        ))
        return self

    def add_method(self):
        """
        Adds POST method to template 
        """
        self.template.add_resource(Method(
            "LambdaApiMethod",
            DependsOn=self.fct_name,
            RestApiId=Ref(self.rest_api),
            AuthorizationType="NONE",
            ResourceId=Ref(self.resource),
            HttpMethod="POST",
            Integration=Integration(
                Credentials=GetAtt(self.execution_role, "Arn"),
                Type="AWS",
                IntegrationHttpMethod='POST',
                IntegrationResponses=[
                    IntegrationResponse(
                        StatusCode='200'
                    )
                ],
                Uri=Join("", [
                    Sub("arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/"),
                    Sub('arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:'),
                    f'function:{self.fct_name}',
                    "/invocations"
                ])
            ),
            MethodResponses=[
                MethodResponse(
                    "CatResponse",
                    StatusCode='200'
                )
            ]
        ))
        return self

    def add_output(self):
        """
        Adds output
        """
        self.template.add_output([
            Output(
                "ApiEndpoint",
                Value=Join("", [
                    "https://",
                    Ref(self.rest_api),
                    ".execute-api.eu-west-1.amazonaws.com/"
                ]),
                Description="Endpoint of the api"
            )
        ])
