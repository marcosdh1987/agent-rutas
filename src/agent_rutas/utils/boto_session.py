import json
import logging
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv(override=True)

logger = logging.getLogger(__name__)


def get_boto3_session(ENV="local"):
    """
    Create a boto3 session based on the environment.

    Parameters:
    - ENV (str): Environment identifier ("local" or "production").

    Returns:
    - boto3.Session: Configured boto3 session object.
    """
    ENV = os.getenv("ENV", "production")
    region = os.getenv("AWS_REGION", "us-east-1")  # Use consistent default
    logger.info(f"Creating boto3 session for environment: {ENV} in region: {region}")
    try:
        if ENV == "local":
            # Use default profile for local environment
            logger.info(
                f"Using profile {os.getenv('AWS_PROFILE', 'default')} for local environment"
            )
            return boto3.Session(
                profile_name=os.getenv("AWS_PROFILE", "default"), region_name=region
            )
        elif ENV == "production":
            # Use explicit credentials for production
            logger.info("Using explicit credentials for production environment")
            access_key = os.getenv("AWS_ACCESS_KEY_ID")
            secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            session_token = os.getenv("AWS_SESSION_TOKEN", None)

            # Validate that the required credentials are set
            if not access_key or not secret_key:
                raise EnvironmentError(
                    "Missing AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY in production"
                )

            # Create session explicitly with credentials
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
                region_name=region,
            )
            logger.info("Successfully created boto3 session for production")
            return session
        else:
            raise ValueError(f"Unknown environment: {ENV}")
    except Exception as e:
        logger.error(f"Error creating boto3 session: {e}")
        raise


def get_boto3_client(service_name, ENV="local"):
    """
    Create a boto3 client for a specific AWS service.

    Parameters:
    - service_name (str): Name of the AWS service for the client (e.g., "s3", "ssm").
    - ENV (str): Environment identifier ("local" or "production").

    Returns:
    - boto3.Client: Configured boto3 client object.
    """
    logging.info(
        f"Creating boto3 client for service: {service_name} in environment: {ENV}"
    )
    if not service_name:
        raise ValueError("service_name is required")

    try:
        # Create a boto3 session and use it to create the client
        session = get_boto3_session(ENV)
        client = session.client(service_name)
        logging.info(f"Successfully created boto3 client for service: {service_name}")
        return client
    except Exception as e:
        logger.error(f"Error creating boto3 client for service {service_name}: {e}")
        raise


def get_ssm_parameter(parameter_name, ENV="local"):
    """
    Retrieve a parameter from AWS SSM Parameter Store.

    Parameters:
    - parameter_name (str): Name of the parameter to retrieve.
    - ENV (str): Environment identifier ("local" or "production").

    Returns:
    - str: The value of the SSM parameter, or None if retrieval fails.
    """
    try:
        ssm = get_boto3_client("ssm", ENV)
        parameter = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return parameter["Parameter"]["Value"]
    except Exception as e:
        logger.error(f"Error getting SSM parameter {parameter_name}: {e}")
        return None


def get_secret(secret_name, key_in_secret: Optional[str] = None, ENV="local"):
    """
    Retrieve a secret from AWS Secrets Manager.

    Parameters:
    - secret_name (str): Name of the secret to retrieve.
    - ENV (str): Environment identifier ("local" or "production").

    Returns:
    - str: The value of the secret, or None if retrieval fails.
    """
    secrets = get_boto3_client("secretsmanager", ENV)
    try:
        response = secrets.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]
    except ClientError as e:
        logger.error(f"Error getting secret {secret_name}: {e}")
        raise e
    if key_in_secret:
        secret = json.loads(secret)[key_in_secret]
    return secret
