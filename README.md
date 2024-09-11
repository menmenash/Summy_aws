# Summy AWS Bot

Summy AWS Bot is a Telegram bot that summarizes articles.
URL\PDF need to be supplied as an input.
Leverages OpenAI's API for text summarization and various AWS services for storage and configuration management.
(Originally written as a self-exercise in using AWS, and because GPT does not allow scraping from social networks).

## Features

- Summarize articles from URLs - Also from LinkdIn, X (Twitter) etc..
- Summarize text from PDF files
- Store and retrieve articles using AWS S3
- Manage bot configuration with AWS DynamoDB
- Secure storage of API keys and tokens using AWS Secrets Manager

## Prerequisites

- Python 3.7+
- AWS account with appropriate permissions
- Telegram Bot Token
- OpenAI API Key

## AWS Services Used

- S3
- DynamoDB
- Secrets Manager
- EC2 (optinal, for easier deployment)

## Installation & Configuration

1. Clone the repository:
   ```
   git clone https://github.com/menmenash/summy_aws.git
   cd summy_aws
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
   
3. Set up AWS services:
   - Configure AWS CLI or set environment variables for AWS access or use EC2 (optional)
   - Create an S3 bucket named `summy-telegrambot-bucket`
   - Create a DynamoDB table named `ConfigTable`
   - Store the following secrets in AWS Secrets Manager:
     - `Telegram_Token`: Your Telegram Bot Token
     - `OpenAI_Token`: Your OpenAI API Key
     - `Telegram_Allowed_Users_ID`: Comma-separated list of allowed Telegram user IDs
       
4. Run main.py in detached mode.
   
## Usage

Summy is at your service!
      - /set <lang> <word limit> [max chars]: Set configuration.
      - /summ <url>: Summarize the article at the given URL.
      - /summ pdf: Summarize an uploaded PDF file.
      - /resp <response>: Get a follow-up response to the last summary.
