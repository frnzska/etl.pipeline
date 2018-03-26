import boto3
import botocore
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)
s3 = boto3.client('s3')

bucket = os.environ['store_bucket']
s3_key = os.environ["s3_key"]


def lambda_handler(event, context):
    """
    Stores source object of stripes webhook event to s3 at 
        given_bucket/given_s3_key/extracted_event_type/extracted_event_id.csv
        Duplicates in event id and type will be overwritten.
    """
    event_type = event['type']
    file_key = f'{s3_key}/{event_type}/{event["id"]}.csv'
    src_obj = event['data']['object']['source']
    df = pd.DataFrame(src_obj, index=[0])
    csv_data = df.to_csv(index=False)

    try:
        s3.put_object(Bucket=bucket,
                      Key=file_key,
                      Body=csv_data.encode())
    except botocore.exceptions.ClientError as e:
        raise e
    return 200
