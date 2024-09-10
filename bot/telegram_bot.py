"""
Telegram Bot

This module contains the TelegramBot class, which handles the main functionality
of the Telegram bot for summarizing articles and PDFs.

Classes:
    TelegramBot: Manages the Telegram bot operations.

Methods:
    __init__(self, token: str, allowed_users: List[int], config_manager: ConfigManager,
             text_extractor: TextExtractor, text_summarizer: TextSummarizer, s3_manager: S3Manager):
        Initializes the TelegramBot with necessary components and configurations.

    setup_handlers(self):
        Sets up the command and message handlers for the bot.

    start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        Handles the /start command.

    help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        Handles the /help command, providing usage instructions.

    set_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        Handles the /set command for updating bot configuration.

    summarize_article(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        Handles the /summ command for summarizing articles from URLs.

    respond_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        Handles the /resp command for follow-up responses to summaries.

    shutdown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        Handles the /shut command for shutting down the bot (authorized users only).

    summarize_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        Handles PDF file uploads for summarization.

    run(self):
        Starts the bot and begins polling for updates.
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from services.config_manager import ConfigManager
from services.text_extractor import TextExtractor
from services.text_summarizer import TextSummarizer
from aws.s3_manager import S3Manager
from utils.telegram_utils import prepare_message_for_telegram
from constants.telegram_constants import TELEGRAM_MESSAGE_SIZE_LIMIT
import sys

class TelegramBot:
    def __init__(self, token, allowed_users, config_manager, text_extractor, text_summarizer, s3_manager):
        self.application = Application.builder().token(token).build()
        self.allowed_users = allowed_users
        self.config_manager = config_manager
        self.text_extractor = text_extractor
        self.text_summarizer = text_summarizer
        self.s3_manager = s3_manager

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("set", self.set_config))
        self.application.add_handler(CommandHandler("summ", self.summarize_article))
        self.application.add_handler(CommandHandler("resp", self.respond_summary))
        self.application.add_handler(CommandHandler("shut", self.shutdown))
        self.application.add_handler(MessageHandler(filters.ALL, self.summarize_pdf))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Hi! Welcome to summy')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "Summy is at your service!\n"
            "- /set <lang> <word limit> [max chars]: Set configuration.\n"
            "- /summ <url>: Summarize the article at the given URL.\n"
            "- /summ pdf: Summarize an uploaded PDF file.\n"
            "- /resp <response>: Get a follow-up response to the last summary.\n"
            "- /shut: Shut down the bot (authorized users only)."
        )
        await update.message.reply_text(help_text)

    async def set_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return

        args = context.args
        if not args or len(args) < 2 or len(args) > 3 or args[0] not in ['heb', 'eng'] or not args[1].isdigit():
            await update.message.reply_text('Please provide valid configuration, i.e., /set <heb/eng> <word limit> [max chars].')
            return

        lang, words_limit = args[0], int(args[1])
        telegram_message_size_limit = int(args[2]) if len(args) == 3 and args[2].isdigit() else TELEGRAM_MESSAGE_SIZE_LIMIT

        if self.config_manager.update_config(lang, words_limit, telegram_message_size_limit):
            await update.message.reply_text('Configuration updated successfully.')
        else:
            await update.message.reply_text('Failed to update configuration.')

    async def summarize_article(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return

        args = context.args
        if not args:
            await update.message.reply_text('Please provide a URL after the command, e.g., /summ <URL>.')
            return

        url = args[0]
        article_text, is_webpage = await self.text_extractor.extract_from_url(url)
        if article_text:
            config = self.config_manager.read_or_initialize_config()
            summary = await self.text_summarizer.summarize(article_text, is_webpage, config)
            await update.message.reply_html(summary)

            self.s3_manager.store_article(article_text)

    async def respond_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return

        args = context.args
        if not args:
            await update.message.reply_text('Please provide a response for the last summary, e.g., /resp <RESPONSE>.')
            return

        config = self.config_manager.read_or_initialize_config()
        user_resp = ' '.join(args)
        
        last_text = self.s3_manager.retrieve_article()
        if not last_text:
            await update.message.reply_text('Failed to retrieve the last article. Please try summarizing a new article.')
            return

        prompt = f"{last_text}\n\n\n\n\n\n{user_resp}\n\n"
        response_text = await self.text_summarizer.respond(prompt, config)
        await update.message.reply_html(response_text)

    async def summarize_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Implementation for PDF summarization
        pass

    async def shutdown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.id not in self.allowed_users:
            await update.message.reply_text("You are not authorized to use this command.")
            return
        await update.message.reply_text("Shutting down the bot. Goodbye!")
        await self.application.stop()
        await self.application.shutdown()
        sys.exit(0)

    def run(self):
        self.setup_handlers()
        self.application.run_polling(stop_signals=None)