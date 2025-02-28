import re
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR)


def clean_text(text, remove_urls=True, remove_special_chars=True):
    """
    Cleans raw text by removing unwanted elements such as HTML tags, URLs, special characters, and extra whitespace.

    Args:
        text (str): The raw text to clean.
        remove_urls (bool): Whether to remove URLs. Default is True.
        remove_special_chars (bool): Whether to remove special characters. Default is True.

    Returns:
        str: The cleaned text.
    """
    # Validate input
    if not isinstance(text, str):
        logging.warning("Invalid input for clean_text: Input must be a string.")
        return ""

    try:
        # Remove HTML tags
        text = re.sub(r'<[^>]*?>', '', text)

        # Remove URLs (optional)
        if remove_urls:
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Remove special characters (optional)
        if remove_special_chars:
            text = re.sub(r'[^a-zA-Z0-9 ]', '', text)

        # Replace multiple spaces with a single space
        text = re.sub(r'\s{2,}', ' ', text)

        # Trim leading and trailing whitespace
        text = text.strip()

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text
    except Exception as e:
        logging.error(f"Error during text cleaning: {e}")
        return ""