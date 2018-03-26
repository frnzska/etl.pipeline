import logging
import os
from sqlalchemy import create_engine
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    Insert into a postgres db staging table given event type.
    If the event is nested it will be flattened.
    """
    engine = create_engine(engine_conf())
    event_type = event["type"].split(".")[0]
    table_name = f'{event_type}_staging'
    event = flatten(event)

    df = pd.DataFrame(event, index=[0])
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
    except Exception as e:
        logger.info(f'Could not connect to {table_name}')
        raise e


def engine_conf():
    """
    Generates db engine config
    :return: (str) db engine conf
    """
    host = os.environ['host']
    port = os.environ['port']
    user = os.environ['user']
    db_name = os.environ['db_name']
    password = os.environ['password']
    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


def flatten(nested_dict, delimiter='_'):
    """
    Flatten nested dictionary
    :param nested_dict: (dict) nested dictionary
    :param delimiter: (str) nested keys connector
    :return: (dict) flat dictionary
    """
    result = {}

    def _f(d, result=result, keys=[]):
        for k, val in d.items():
            if not isinstance(val, dict):
                key = delimiter.join(keys + [k]) if keys else k
                result[key] = val
            else:
                _f(val, result, keys + [k])

    _f(nested_dict)
    return result
