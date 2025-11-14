# commands/web_automation/gehu_automation.py

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from google.genai import types


def get_webdriver():

    options = ChromeOptions()
    # Keeps the browser window open after the script finishes its execution
    options.add_experimental_option("detach", True)

    # Selenium Manager will automatically find and manage the ChromeDriver.
    service = ChromeService()

    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        print("WebDriver launched a new Chrome instance successfully.")
        return driver
    except WebDriverException as e:
        print(f"Failed to launch new Chrome instance: {e}")
        print("Please ensure:")
        print("1. Your Chrome browser is installed and up-to-date.")
        print("2. Your 'selenium' library is updated (pip install --upgrade selenium).")
        raise  # Re-raise the exception after printing debug info


# --- Internal Helper Function to Scrape Dynamic Web Content ---
def _scrape_single_url_content(url: str) -> dict:
    """
    Internal helper to scrape content from a given URL using Selenium.
    Returns the extracted text or an error message.
    """
    if not urlparse(url).scheme:
        url = "http://" + url

    driver = None
    try:
        driver = get_webdriver()
        print(f"  [Scraper]: Navigating to {url} for content extraction...")
        driver.get(url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("  [Scraper]: Page loaded. Extracting content...")

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Remove script, style, and other non-content elements for cleaner text
        for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside", "form", "svg"]):
            script_or_style.extract()

        # Get all text from paragraphs, headings, and list items
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'title'])

        extracted_text = []
        for element in text_elements:
            cleaned_text = element.get_text(separator=' ', strip=True)
            if cleaned_text:
                extracted_text.append(cleaned_text)

        full_text = "\n\n".join(extracted_text)

        if len(full_text) > 10000:
            full_text = full_text[:10000] + "\n\n[... content truncated for brevity ...]"

        if not full_text.strip():
            return {"success": False, "message": "Could not extract significant text content from the notice page."}

        print(f"  [Scraper]: Successfully extracted content. Length: {len(full_text)} characters.")
        return {"success": True, "content": full_text}

    except TimeoutException:
        return {"success": False,
                "message": f"Timed out waiting for notice page elements to load on {url}. It might be too slow or blocked."}
    except WebDriverException as e:
        return {"success": False, "message": f"WebDriver error during content scraping of {url}: {e}"}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred during content scraping of {url}: {e}"}
    finally:

        if driver:
            pass  # driver.quit() # Uncomment this if you want it to close automatically


# --- Function: Open GEHU B.Tech Notice and Return Content ---
def open_gehu_btech_notice_and_return_content() -> dict:

    driver = None
    try:
        # Get a WebDriver instance to navigate to the main GEHU page
        driver = get_webdriver()

        print("Directly navigating to http://btechcsegehu.in/...")
        driver.get("http://btechcsegehu.in/")

        # 1. Wait for the main GEHU page to load and find the 'Latest Notices' section
        print("Waiting for 'Latest Notices' section on GEHU website (id='recent-posts-4')...")
        latest_notices_section = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "recent-posts-4"))
        )
        print("Found 'Latest Notices' section.")

        # 2. Get the first notice's title and URL
        print(
            "Waiting for the first notice link within 'Latest Notices' (//aside[@id='recent-posts-4']//ul/li[1]/a)...")
        first_notice_xpath = "//aside[@id='recent-posts-4']//ul/li[1]/a"

        first_notice_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, first_notice_xpath))
        )

        notice_title = first_notice_element.text.strip()
        notice_url = first_notice_element.get_attribute('href')

        print(f"Identified first notice: '{notice_title}' with URL: {notice_url}")

        # 3. Scrape content from the notice URL using the helper function
        print(f"Proceeding to scrape content from the notice URL: {notice_url}")
        scrape_result = _scrape_single_url_content(notice_url)

        if scrape_result.get("success"):
            return {
                "success": True,
                "notice_title": notice_title,
                "scraped_content": scrape_result.get("content"),
                "message": "Successfully retrieved notice title and scraped its content for summarization."
            }
        else:
            return {
                "success": False,
                "message": f"Could not scrape content from notice URL '{notice_url}': {scrape_result.get('message', 'Unknown scraping error')}",
                "notice_title": notice_title,
                "scraped_content": ""
            }

    except TimeoutException as e:
        return {"success": False,
                "message": f"Timed out waiting for an element on GEHU website. Website layout might have changed or internet is slow. Error: {e}"}
    except NoSuchElementException as e:
        return {"success": False,
                "message": f"Could not find a required element ('Latest Notices' section or first notice link). Website layout might have changed. Error: {e}"}
    except WebDriverException as e:
        return {"success": False, "message": f"WebDriver error during GEHU automation: {e}"}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred during GEHU automation: {e}"}
    finally:
        # The main driver instance should also remain open if detach=True
        pass


# --- Function Declaration (Schema) for Gemini ---
open_gehu_btech_notice_and_return_content_schema_dict = types.FunctionDeclaration(
    name="open_gehu_btech_notice_and_return_content",
    description="Directly navigates to 'http://btechcsegehu.in/', identifies the latest notice, scrapes its content, and returns the notice's title and full content for summarization.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},  # No parameters
        required=[]
    )
)