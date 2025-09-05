import boto3
import json
import os
import logging
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AWSSecretsManager:
    def __init__(self, secret_name: str = "rmgx-secrets", region_name: str = "ap-south-1"):
        self.secret_name = secret_name
        self.region_name = region_name
        self.client = None

    def _initialize_client(self):
        """Initialize AWS Secrets Manager client"""
        try:
            session = boto3.session.Session()
            self.client = session.client(
                service_name='secretsmanager',
                region_name=self.region_name
            )
            return True
        except (NoCredentialsError, PartialCredentialsError) as e:
            logger.warning(f"AWS credentials not found or incomplete: {str(e)}")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize AWS Secrets Manager client: {str(e)}")
            return False

    def fetch_secrets(self) -> Optional[Dict[str, str]]:
        """
        Fetch secrets from AWS Secrets Manager
        Returns dictionary of secrets if successful, None if failed
        """
        if not self._initialize_client():
            return None

        try:
            logger.info(f"Attempting to fetch secrets from AWS Secrets Manager: {self.secret_name}")

            get_secret_value_response = self.client.get_secret_value(
                SecretId=self.secret_name
            )

            secret_string = get_secret_value_response['SecretString']

            # Parse the secret string (assuming it's JSON format)
            try:
                secrets = json.loads(secret_string)
                logger.info(f"Successfully fetched {len(secrets)} secrets from AWS Secrets Manager")
                return secrets
            except json.JSONDecodeError:
                # If it's not JSON, treat it as a single secret
                logger.info("Fetched single secret value from AWS Secrets Manager")
                return {"SECRET_VALUE": secret_string}

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'DecryptionFailureException':
                logger.error("Secrets Manager can't decrypt the protected secret text using the provided KMS key.")
            elif error_code == 'InternalServiceErrorException':
                logger.error("An error occurred on the server side.")
            elif error_code == 'InvalidParameterException':
                logger.error("Invalid parameter provided to Secrets Manager.")
            elif error_code == 'InvalidRequestException':
                logger.error("Invalid request to Secrets Manager.")
            elif error_code == 'ResourceNotFoundException':
                logger.warning(f"Secret '{self.secret_name}' not found in AWS Secrets Manager.")
            else:
                logger.error(f"AWS Secrets Manager error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching secrets from AWS Secrets Manager: {str(e)}")

        return None

    def set_environment_variables(self, secrets: Dict[str, str]) -> None:
        """Set environment variables from fetched secrets"""
        for key, value in secrets.items():
            os.environ[key] = str(value)
            logger.debug(f"Set environment variable: {key}")

def load_secrets_with_fallback() -> bool:
    """
    Load secrets from AWS Secrets Manager with local fallback
    Returns True if AWS secrets were loaded, False if using local
    """
    secrets_manager = AWSSecretsManager()

    # Try to fetch secrets from AWS
    secrets = secrets_manager.fetch_secrets()

    if secrets:
        # Set environment variables from AWS secrets
        secrets_manager.set_environment_variables(secrets)
        logger.info("✅ Environment variables loaded from AWS Secrets Manager")
        return True
    else:
        logger.info("⚠️  AWS Secrets Manager not available, using local environment variables")
        return False
