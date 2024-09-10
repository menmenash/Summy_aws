"""
Secret Manager

This module contains the SecretManager class, which is responsible for retrieving secrets from AWS Secrets Manager.

Classes:
    SecretManager: Manages interactions with AWS Secrets Manager.

Methods:
    __init__(self, region_name: str = 'eu-north-1'):
        Initializes the SecretManager with the specified AWS region.

    get_secret(self, secret_name: str) -> dict:
        Retrieves a secret from AWS Secrets Manager.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            dict: The secret value as a dictionary.

        Raises:
            ClientError: If there's an error retrieving the secret from AWS Secrets Manager.
            ValueError: If the retrieved secret does not contain a SecretString.

Attributes:
    session (boto3.session.Session): The boto3 session used for AWS interactions.
    client (boto3.client): The boto3 client for AWS Secrets Manager.

Note:
    This class requires appropriate AWS permissions to access Secrets Manager.
"""

import boto3
from botocore.exceptions import ClientError
import json
import logging

logger = logging.getLogger(__name__)

class SecretManager:
    def __init__(self, region_name: str = 'eu-north-1'):
        self.session = boto3.session.Session()
        self.client = self.session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

    def get_secret(self, secret_name: str) -> dict:
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
            raise
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return json.loads(secret)
            else:
                logger.error(f"Secret {secret_name} does not contain a SecretString")
                raise ValueError(f"Secret {secret_name} does not contain a SecretString")