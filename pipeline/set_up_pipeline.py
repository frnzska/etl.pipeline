import yaml
import subprocess
from cfn_stack_builder.lambda_stack_gen import LambdaTemplate
from cfn_stack_builder.api_gateway_stack_gen import ApiGatewayTemplate
from cfn_stack_builder.statemachine_stack_gen import StatemachineTemplate
from cfn_stack_builder.iam_policies import (logging_policy, invoke_state_machine_policy, s3_access_policy,
                                            invoke_lambda_policy)

with open('pipeline/config.yml', 'r') as f:
    CONFIG = yaml.load(f)


# Get all settings
S3_BUCKET = CONFIG['S3LambdaDeploymentBucket']
REGION = CONFIG['region']
ACCOUNT_NR = CONFIG['account_nr']

# stepfunctions
PERSIST_RDS_LAMBDA_ARGS = CONFIG['PersistRdsLambda']
persist_rds_lambda_policies = [logging_policy]
persist_rds_lambda = LambdaTemplate(**PERSIST_RDS_LAMBDA_ARGS, s3_bucket=S3_BUCKET,
                                    policies=persist_rds_lambda_policies)

STORE_S3_LAMBDA_ARGS = CONFIG['StoreS3Lambda']
store_s3_lambda_policies = [logging_policy, s3_access_policy]
store_s3_lambda = LambdaTemplate(**STORE_S3_LAMBDA_ARGS, s3_bucket=S3_BUCKET,
                                 policies=store_s3_lambda_policies)

# statemachine
STATEMACHINE_ARGS = CONFIG['Statemachine']
statemachine_policies = [logging_policy, invoke_lambda_policy]
stp_fct_names = [CONFIG['PersistRdsLambda']['fct_name'], CONFIG['StoreS3Lambda']['fct_name']]
statemachine = StatemachineTemplate(**STATEMACHINE_ARGS,
                                    lambda_names=stp_fct_names,
                                    policies=statemachine_policies,
                                    region=REGION,
                                    account_nr=ACCOUNT_NR)

# api gateway resources
API_LAMBDA_ARGS = CONFIG['ApiLambda']
API_GATE_ARGS = CONFIG['ApiGateway']
api_lambda_policies = [logging_policy, invoke_state_machine_policy, invoke_lambda_policy]

API_GATE_ARGS['env_vars'] = {'statemachine_name': STATEMACHINE_ARGS['name']}
api_gateway_resources = ApiGatewayTemplate(**API_GATE_ARGS, **API_LAMBDA_ARGS,
                            s3_bucket=S3_BUCKET,
                            policies=api_lambda_policies)


def deploy_zipped_lambdas_to_s3():
    """
    Deploys zipped lambdas to s3
    """

    subprocess.call(f"./pipeline/deploy_zipped_lambdas_to_s3.sh {S3_BUCKET}", shell=True)


def create_pipeline():
    """
    Create pipeline infrastructure 
    """
    persist_rds_lambda.create_stack()
    store_s3_lambda.create_stack()
    statemachine.create_stack()
    api_gateway_resources.create_stack()


def destroy_all():
    """
    Destroy pipeline infrastructure
    """
    persist_rds_lambda.delete_stack()
    store_s3_lambda.delete_stack()
    statemachine.delete_stack()
    api_gateway_resources.delete_stack()


#### execute ####
#### 1. Step:  Deploy zipped lambdas to s3 with
# deploy_zipped_lambdas_to_s3()

#### 2. Step: build all resources with
# create_pipeline()

#### Delete all with
# destroy_all()
