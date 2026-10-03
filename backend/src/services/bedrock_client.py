"""
Bedrock Runtime Client for INVOX.

Provides a clean interface for invoking Amazon Bedrock models
for order extraction. Designed to be testable via mocking.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


@dataclass
class BedrockConfig:
    """Configuration for Bedrock client."""
    model_id: str
    region: str
    max_tokens: int = 1024
    temperature: float = 0.0
    top_p: float = 0.1


@dataclass
class BedrockResponse:
    """Parsed response from Bedrock."""
    success: bool
    content: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


def get_bedrock_config() -> BedrockConfig:
    """
    Get Bedrock configuration from environment variables.
    
    Environment variables:
    - BEDROCK_MODEL_ID: Model ID to use (default: India Claude Haiku 4.5 profile)
    - BEDROCK_REGION: Region for the Bedrock Runtime client
    - BEDROCK_MAX_TOKENS: Max tokens for response (default: 1024)
    - BEDROCK_TEMPERATURE: Temperature for generation (default: 0.0)
    """
    model_id = os.environ.get(
        'BEDROCK_MODEL_ID',
        'in.anthropic.claude-haiku-4-5-20251001-v1:0',
    )
    region = os.environ.get(
        'BEDROCK_REGION',
        os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'ap-south-1')),
    )
    max_tokens = int(os.environ.get('BEDROCK_MAX_TOKENS', '1024'))
    temperature = float(os.environ.get('BEDROCK_TEMPERATURE', '0.0'))
    top_p = float(os.environ.get('BEDROCK_TOP_P', '0.1'))
    
    return BedrockConfig(
        model_id=model_id,
        region=region,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )


class BedrockClient:
    """
    Client for invoking Bedrock models.
    
    Isolated for easy mocking in tests. The actual boto3 client
    is created lazily to allow configuration override in tests.
    """
    
    def __init__(self, config: Optional[BedrockConfig] = None, client=None):
        """
        Initialize Bedrock client.
        
        Args:
            config: BedrockConfig object. If None, reads from environment.
            client: Pre-created boto3 client (for testing/mocking).
        """
        self.config = config or get_bedrock_config()
        self._client = client
    
    @property
    def client(self):
        """Lazily create boto3 client if not injected."""
        if self._client is None:
            self._client = boto3.client('bedrock-runtime', region_name=self.config.region)
        return self._client
    
    def invoke_model(self, prompt: str) -> BedrockResponse:
        """
        Invoke the Bedrock model with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            BedrockResponse with success status and content or error details
        """
        # Build the request body for Anthropic Claude models
        body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
            'top_p': self.config.top_p,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt,
                }
            ],
        }
        
        try:
            response = self.client.invoke_model(
                modelId=self.config.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json',
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract content from Anthropic response format
            content = None
            if 'content' in response_body and len(response_body['content']) > 0:
                content = response_body['content'][0].get('text', '')
            
            return BedrockResponse(
                success=True,
                content=content,
                raw_response=response_body,
            )
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'UNKNOWN')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Bedrock ClientError: {error_code} - {error_message}")
            
            # Map common Bedrock errors to our error codes
            if error_code == 'ThrottlingException':
                return BedrockResponse(
                    success=False,
                    error_code='BEDROCK_THROTTLED',
                    error_message='Bedrock request was throttled',
                )
            elif error_code == 'ValidationException':
                return BedrockResponse(
                    success=False,
                    error_code='BEDROCK_VALIDATION_ERROR',
                    error_message=f'Bedrock validation error: {error_message}',
                )
            elif error_code == 'ModelNotReadyException':
                return BedrockResponse(
                    success=False,
                    error_code='BEDROCK_MODEL_NOT_READY',
                    error_message='Bedrock model is not ready',
                )
            elif error_code == 'AccessDeniedException':
                return BedrockResponse(
                    success=False,
                    error_code='BEDROCK_ACCESS_DENIED',
                    error_message='Access denied to Bedrock model',
                )
            else:
                return BedrockResponse(
                    success=False,
                    error_code='BEDROCK_CLIENT_ERROR',
                    error_message=f'Bedrock error: {error_message}',
                )
                
        except BotoCoreError as e:
            logger.error(f"Bedrock BotoCoreError: {type(e).__name__}: {e}")
            return BedrockResponse(
                success=False,
                error_code='BEDROCK_CONNECTION_ERROR',
                error_message='Failed to connect to Bedrock service',
            )
            
        except Exception as e:
            logger.error(f"Bedrock unexpected error: {type(e).__name__}: {e}")
            return BedrockResponse(
                success=False,
                error_code='BEDROCK_UNEXPECTED_ERROR',
                error_message='Unexpected error invoking Bedrock',
            )


def create_bedrock_client(config: Optional[BedrockConfig] = None, client=None) -> BedrockClient:
    """
    Factory function to create Bedrock client.
    
    Allows easy mocking in tests by passing a mock client.
    """
    return BedrockClient(config=config, client=client)