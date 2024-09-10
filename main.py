"""
Summy AWS Test   

This script sets up and runs a Telegram bot that summarizes articles and PDFs using AWS services.

The bot uses the following AWS services:
- S3: For storing and retrieving articles
- DynamoDB: For managing configuration
- Secrets Manager: For securely storing API keys and tokens

The main components of the system are:
1. TelegramBot: Handles user interactions and commands
2. ConfigManager: Manages bot configuration using DynamoDB
3. TextExtractor: Extracts text from URLs and PDFs
4. TextSummarizer: Summarizes extracted text using OpenAI's API
5. S3Manager: Handles storing and retrieving articles from S3
6. SecretManager: Retrieves secrets from AWS Secrets Manager

Usage:
    Run this script to start the Telegram bot. Ensure all required AWS credentials
    and configurations are set up beforehand.

Note:
    This script requires various AWS permissions to be
    set up correctly. Refer to AWS Documentation in case of PermissionsError0s
"""

import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.telegram_bot import TelegramBot
from services.config_manager import ConfigManager
from services.text_extractor import TextExtractor
from services.text_summarizer import TextSummarizer
from aws.secret_manager import SecretManager
from aws.s3_manager import S3Manager
from aws.dynamodb_manager import DynamoDBManager
import boto3

def main():
    # Setup AWS clients
    s3_client = boto3.client('s3')
    
    # Get secrets
    secret_manager = SecretManager()
    telegram_secrets = secret_manager.get_secret('Telegram_Token')
    openai_secret = secret_manager.get_secret('OpenAI_Token')
    allowed_users_str = secret_manager.get_secret('Telegram_Allowed_Users_ID')

    # Setup services
    dynamodb_manager = DynamoDBManager('ConfigTable')
    config_manager = ConfigManager(dynamodb_manager)
    text_extractor = TextExtractor()
    text_summarizer = TextSummarizer(openai_secret['OpenAI_Token'])
    s3_manager = S3Manager(s3_client, 'summy-telegrambot-bucket')

    # Setup bot
    bot = TelegramBot(
        token=telegram_secrets['Telegram_Token'],
        allowed_users=[int(id.strip()) for id in allowed_users_str['Telegram_Allowed_Users_ID'].split(',') if id.strip()],
        config_manager=config_manager,
        text_extractor=text_extractor,
        text_summarizer=text_summarizer,
        s3_manager=s3_manager
    )
    
    bot.run()

if __name__ == '__main__':
    main()