"""
Config Manager

This module contains the ConfigManager class, which is responsible for managing
the configuration settings of the application using DynamoDB.

Classes:
    ConfigManager: Manages configuration settings using DynamoDB.

Methods:
    __init__(self, dynamodb_manager):
        Initializes the ConfigManager with a DynamoDB manager.

    read_or_initialize_config(self) -> Dict[str, Any]:
        Reads the configuration from DynamoDB or initializes it with default values.

    update_config(self, lang: str, words_limit: int, telegram_message_size_limit: int = 4096) -> bool:
        Updates the configuration settings in DynamoDB.

Attributes:
    db_manager: An instance of DynamoDBManager for database operations.
    default_config: A dictionary containing default configuration values.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, dynamodb_manager):
        self.db_manager = dynamodb_manager
        self.default_config = {
            'lang': 'eng',
            'words_limit': 300,
            'telegram_message_size_limit': 4096
        }

    def read_or_initialize_config(self) -> Dict[str, Any]:
        config = {}
        for key in self.default_config.keys():
            value = self.db_manager.get_item(key)
            if value is None:
                value = self.default_config[key]
                self.db_manager.put_item(key, value)
            config[key] = value
        return config

    def update_config(self, lang: str, words_limit: int, telegram_message_size_limit: int = 4096) -> bool:
        if lang not in ['eng', 'heb']:
            raise ValueError("Language must be either 'eng' or 'heb'")
        if not isinstance(words_limit, int) or words_limit < 0 or words_limit > 1000:
            raise ValueError("words_limit must be an integer between 0 and 1000")
        if not isinstance(telegram_message_size_limit, int) or telegram_message_size_limit < 1 or telegram_message_size_limit > 4096:
            raise ValueError("telegram_message_size_limit must be an integer between 1 and 4096")

        success = all([
            self.db_manager.put_item('lang', lang),
            self.db_manager.put_item('words_limit', str(words_limit)),
            self.db_manager.put_item('telegram_message_size_limit', telegram_message_size_limit)
        ])
        return success