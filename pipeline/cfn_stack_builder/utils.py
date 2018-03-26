import boto3
import botocore
import logging

logger = logging.getLogger(__name__)

cfn = boto3.client('cloudformation')


def build(*, stack_name, template):
    """
    Build stack resources defined in template for given stack_name
    :param stack_name: (str) name of the stack
    :param template: (troposphere.template)
    :return: 
    """
    template_json = template.to_json(indent=4)
    cfn.validate_template(TemplateBody=template_json)
    stack = {}
    stack['StackName'] = stack_name
    stack['TemplateBody'] = template_json
    stack['Capabilities'] = ['CAPABILITY_NAMED_IAM']
    try:
        cfn.create_stack(**stack)
    except botocore.exceptions.ClientError as e:
        logger.error(e)
        raise e
    logger.info(f'building {stack_name}')


def delete(*, stack_name):
    """
    Delete stack resources
    :param stack_name: 
    """
    try:
        cfn.delete_stack(StackName=stack_name)
    except botocore.exceptions.ClientError as e:
        logger.error(e)
        raise e
