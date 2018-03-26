"""
Creates Stepfunction Statemachine Template
"""

import json
import logging
from awacs.sts import AssumeRole
from troposphere import iam, stepfunctions, Template, GetAtt, Sub
from awacs.aws import Allow, Policy, Principal, Statement
from cfn_stack_builder.utils import build, delete

logger = logging.getLogger(__name__)


class StatemachineTemplate:
    def __init__(self, *, stage, name, account_nr, region, lambda_names, policies):
        """
        Aws stepfunction statemachine
        :param stage: (str) development stage
        :param name: (str) name of statemachine
        :param account_nr: (str) aws account number
        :param region: (str) aws region
        :param lambda_names: (list(str)) names of stepfunctions
        :param policies:  (list(iam.policies)) needed iam policies
        """
        self.template = Template()
        self.name = name
        self.stack_name = f'{name}-{stage}'
        self.region = region
        self.account_nr = account_nr
        self.policies = policies
        self.execution_role = None
        self.definition_string = json.dumps({
            "StartAt": "StoreData",
            "States": {
                "StoreData": {
                    "Type": "Parallel",
                    "End": True,
                    "Branches": [
                        {
                            "StartAt": f"{lambda_name}",
                            "States": {
                                f"{lambda_name}": {
                                    "Type": "Task",
                                    "Resource":
                                        f"arn:aws:lambda:{region}:{account_nr}:function:{lambda_name}",
                                    "End": True
                                }
                            }
                        } for lambda_name in lambda_names
                    ]
                }
            }
        })

    def create_stack(self):
        """
        Generate template components and create template resources
        """
        self.add_execution_role() \
            .add_statemachine_resource()

        build(stack_name=self.stack_name, template=self.template)

    def delete_stack(self):
        """
        Delete stack resources
        """
        delete(stack_name=self.stack_name)

    def add_execution_role(self):
        """
        Adds execution role to statemachine template
        """
        execution_role = self.template.add_resource(
            iam.Role(
                f'{self.name}ExecutionRole',
                RoleName=f'{self.stack_name}-ExecutionRole',
                Policies=self.policies,
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", [f"states.{self.region}.amazonaws.com"])
                        )
                    ]
                ),
            )
        )
        self.execution_role = execution_role
        return self

    def add_statemachine_resource(self):
        """
        Adds stepfunction statemachine to template
        """
        self.template.add_resource(
            stepfunctions.StateMachine(
                f'{self.name}',
                DefinitionString=self.definition_string,
                RoleArn=GetAtt(self.execution_role, 'Arn'),
            )
        )
