"""
Text Summarizer

This module contains the TextSummarizer class, which is responsible for summarizing text and generating responses using OpenAI's API.

Classes:
    TextSummarizer: Summarizes text and generates responses using OpenAI's API.

Methods:
    __init__(self, openai_api_key: str):
        Initializes the TextSummarizer with the provided OpenAI API key.

    async summarize(self, text: str, is_webpage: bool, config: dict) -> str:
        Summarizes the given text using OpenAI's API.

        Args:
            text (str): The text to be summarized.
            is_webpage (bool): Indicates whether the text is from a webpage.
            config (dict): Configuration parameters for the summary.

        Returns:
            str: The generated summary, prepared for Telegram message format.

    async respond(self, prompt: str, config: dict) -> str:
        Generates a response to the given prompt using OpenAI's API.

        Args:
            prompt (str): The prompt to generate a response for.
            config (dict): Configuration parameters for the response.

        Returns:
            str: The generated response, prepared for Telegram message format.

Note:
    This class uses the OpenAIUtils class for API interactions with OpenAI.
"""

from utils.openai_utils import OpenAIUtils
from utils.telegram_utils import prepare_message_for_telegram

class TextSummarizer:
    def __init__(self, openai_api_key: str):
        self.openai_utils = OpenAIUtils(openai_api_key)

    async def summarize(self, text: str, is_webpage: bool, config: dict) -> str:
        summary = self.openai_utils.get_openai_summary(text, is_webpage, config)
        return prepare_message_for_telegram(summary, config['telegram_message_size_limit'])

    async def respond(self, prompt: str, config: dict) -> str:
        response = self.openai_utils.get_openai_response(prompt, config)
        return prepare_message_for_telegram(response, config['telegram_message_size_limit'])