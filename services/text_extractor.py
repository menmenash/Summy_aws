"""
Text Extractor

This module contains the TextExtractor class, which is responsible for extracting text from URLs and PDF files.

Classes:
    TextExtractor: Extracts text from URLs and PDF files.

Methods:
    extract_from_url(url: str) -> Tuple[str, bool]:
        Asynchronously extracts text content from a given URL.

        Args:
            url (str): The URL to extract text from.

        Returns:
            Tuple[str, bool]: A tuple containing the extracted text and a boolean indicating
                              whether it's the full page content or just the article body.

    extract_from_pdf(pdf_file: BytesIO) -> str:
        Extracts text content from a PDF file.

        Args:
            pdf_file (BytesIO): A BytesIO object containing the PDF file.

        Returns:
            str: The extracted text from the PDF.
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from io import BytesIO
from typing import Tuple

class TextExtractor:
    @staticmethod
    async def extract_from_url(url: str) -> Tuple[str, bool]:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(10000)
            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            article_body = soup.find('article') or soup.find('div', class_='article-content') or soup.find('main')
            if article_body:
                text = " ".join(article_body.stripped_strings)
                is_full_page = False
            else:
                text = " ".join(soup.stripped_strings)
                is_full_page = True

            return text, is_full_page

    @staticmethod
    def extract_from_pdf(pdf_file: BytesIO) -> str:
        return extract_text(pdf_file)