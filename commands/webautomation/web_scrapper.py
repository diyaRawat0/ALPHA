# commands/web_automation/web_scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from google.genai import types


def scrape_website_content(url: str) -> dict:
    """
    Scrapes the main textual content from a given website URL.
    This function focuses on extracting visible text from paragraphs, headings, and lists.
    It returns the extracted text or an error message.
    """
    # Basic URL validation
    if not urlparse(url).scheme:
        url = "http://" + url  # Prepend http if no scheme is provided

    print(f"Attempting to scrape content from: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements to clean up text
        for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside", "form"]):
            script_or_style.extract()

        # Get all text from paragraphs, headings, and list items
        # Consider using a more sophisticated text extraction library for complex sites if needed
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'title'])

        extracted_text = []
        for element in text_elements:
            # Clean up whitespace and ensure text is not empty
            cleaned_text = element.get_text(separator=' ', strip=True)
            if cleaned_text:
                extracted_text.append(cleaned_text)

        # Join the text with double newlines for better readability
        full_text = "\n\n".join(extracted_text)

        # Limit the text length to avoid hitting Gemini's context window limits
        # (Approx 100,000 characters for Gemini 1.5 Pro, 32,000 for 1.0 Pro, 8,000 for Flash)
        # We'll truncate to a reasonable amount, like 10,000 characters for safety
        if len(full_text) > 10000:
            full_text = full_text[:10000] + "\n\n[... content truncated for length ...]"

        if not full_text.strip():
            return {"success": False, "message": "Could not extract significant text content from the page."}

        print(f"Successfully scraped content from {url}. Length: {len(full_text)} characters.")
        return {"success": True, "content": full_text}

    except requests.exceptions.Timeout:
        return {"success": False, "message": f"Timeout: The request to {url} took too long."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "message": f"HTTP Error {e.response.status_code} for {url}: {e.response.reason}"}
    except requests.exceptions.RequestException as e:
        return {"success": False,
                "message": f"Network Error: Could not connect to {url}. Check URL or internet connection. Details: {e}"}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred during scraping {url}: {e}"}


# --- Function Declaration (Schema) for Gemini ---
scrape_website_content_schema_dict = types.FunctionDeclaration(
    name="scrape_website_content",
    description="Scrapes the main textual content from a given website URL and returns it for summarization or analysis. It handles basic URL validation and extracts visible text.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "url": types.Schema(
                type=types.Type.STRING,
                description="The full URL of the website to scrape (e.g., 'https://www.example.com/article')."
            )
        },
        required=["url"]
    )
)