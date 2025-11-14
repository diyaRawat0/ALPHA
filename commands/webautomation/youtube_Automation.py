import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# New import for Chrome service and options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

# For FunctionDeclaration
from google.genai import types


def get_webdriver():

    try:
        # Selenium Manager will automatically find and manage the ChromeDriver.
        service = ChromeService()  # No path needed for automatic management
        options = ChromeOptions()
        options.add_argument("--incognito")
        # options.add_argument("--headless") # Uncomment this to run browser in background
        options.add_experimental_option("detach", True)  # Keep browser open after script finishes
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        print("WebDriver initialized successfully (likely via Selenium Manager).")
        return driver
    except WebDriverException as e:
        print(f"Failed to initialize WebDriver: {e}")
        print("Please ensure:")
        print("1. Google Chrome browser is installed and up-to-date.")
        print("2. Your 'selenium' library is updated (pip install --upgrade selenium).")
        print("3. If using an older Selenium version (<4.6) or a non-standard Chrome install,")
        print("   ensure ChromeDriver version matches your Chrome browser version and its path is correct.")
        raise  # Re-raise the exception after printing debug info

def open_youtube_trending() -> dict:
    """
    Opens YouTube in the default web browser and attempts to play the top trending video.
    """
    driver = None
    try:
        driver = get_webdriver()
        print("Navigating to YouTube...")
        driver.get("https://www.youtube.com/feed/trending")  # Corrected URL for trending

        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "contents"))
        )
        print("YouTube page loaded.")

        first_video_xpath = '(//ytd-video-renderer)[1]//a[@id="thumbnail"]'
        video_thumbnail = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, first_video_xpath))
        )
        video_title = video_thumbnail.get_attribute("title") if video_thumbnail.get_attribute("title") else "the video"
        print(f"Clicking on video: '{video_title}'")
        video_thumbnail.click()

        return {"success": True, "message": f"Opened YouTube and started playing '{video_title}'."}

    except TimeoutException:
        return {"success": False,
                "message": "Timed out waiting for YouTube elements to load. YouTube layout might have changed or internet is slow."}
    except NoSuchElementException:
        return {"success": False,
                "message": "Could not find video elements on YouTube trending page. YouTube layout might have changed."}
    except WebDriverException as e:
        return {"success": False, "message": f"WebDriver error during YouTube automation: {e}"}
    except Exception as e:
        return {"success": False, "message": f"An unexpected error occurred during YouTube automation: {e}"}
    finally:
        # Keeping the browser open for easy testing and debugging.
        # If you want the browser to close automatically after the function, uncomment:
        # if driver:
        #     driver.quit()
        pass

# --- Function Declaration (Schema) for Gemini ---
open_youtube_trending_schema_dict = types.FunctionDeclaration(
    name="open_youtube_trending",
    description="Opens the default web browser to YouTube and attempts to play the top trending video.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},  # No parameters needed
        required=[]
    )
)