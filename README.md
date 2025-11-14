# ALPHA: Python Assistant 🤖

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat&logo=python)](https://www.python.org/)
[![Google Gemini API](https://img.shields.io/badge/Powered%20by-Gemini-orange.svg?style=flat&logo=google)](https://ai.google.dev/gemini)
[![Rich Terminal](https://img.shields.io/badge/Terminal%20UI-Rich-brightgreen.svg?style=flat&logo=python)](https://github.com/Textualize/rich)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ## ✨ Introduction

**ALPHA** is an intelligent, conversational AI assistant designed to simplify your daily computing and web tasks through natural language commands. Leveraging a robust function-calling mechanism, ALPHA acts as your personal command-line interface, automating common operations on your local machine and interacting with web services.

Say goodbye to complex commands and hello to intuitive, human-like interaction!

## 🚀 Features

* **Conversational AI Interface:** Interact with the assistant using plain English, just like you would with a human.
* **Intelligent Function Calling:** Automatically maps your requests to pre-defined Python functions (tools) to execute tasks.
* **Dynamic Command Execution:** No need to remember specific syntax; the AI understands your intent and runs the appropriate script.
* **Enhanced User Experience:** Utilizes the `rich` library for beautiful, colored, and structured terminal output, making interactions clear and engaging.

### 🗂️ Core Capabilities (Commands)

ALPHA can currently perform a wide range of tasks, including but not limited to:

* **Folder & File Management:**
    * Create new folders (e.g., "Create a folder named 'MyNewProject' in 'C:\\Users\\your_name\\Documents'").
    * Delete existing folders (e.g., "Remove the directories 'old_data' and 'temp_backup'").
    * Move folders from one location to another (e.g., "Move 'C:\\Downloads\\installer' to 'D:\\Software'").
    * Rename folders (e.g., "Rename the directory 'photos_2023' to 'photos_archive'").
* **Python File Creation:**
    * Generate Python scripts with specified content (e.g., "Create a Python file named 'hello.py' at 'C:\\Scripts' with content: `print('Hello, World!')`").
* **Website Management:**
    * Create basic HTML websites (e.g., "Create a website for my new startup named 'InnovateTech'").
    * Open local HTML web pages (e.g., "Open the website located at 'C:\\MyWebsites\\project\\index.html'").
* **Web Automation & Information Retrieval:**
    * Open YouTube's trending videos (e.g., "Show me what's popular on YouTube.").
    * Scrape content from specified URLs (e.g., "Scrape the content from 'https://www.example.com/'").
    * Access specific university notices (e.g., "Get the latest B.Tech notices from GEHU.").


## 🛠️ Installation

Follow these steps to set up ALPHA on your local machine.

### Prerequisites

* **Python 3.8+** (Recommended: Python 3.10 or newer)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone

2.  **Create a virtual environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    * **Windows (PowerShell):**
        ```bash
        .\.venv\Scripts\activate
        ```
    * **Windows (Command Prompt):**
        ```bash
        .venv\Scripts\activate.bat
        ```
    * **Linux / macOS:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    Create a `requirements.txt` file in your project root with the following content (and add any other libraries your `commands` modules might require, e.g., `requests`, `beautifulsoup4`, `selenium`, `pandas`):

    ```txt
    google-generativeai # Specific version like ==0.5.0 if needed
    rich # Specific version like ==13.0.0 if needed
    # Add other dependencies used in your 'commands' modules here, e.g.:
    # requests
    # beautifulsoup4
    # selenium # if you use a browser driver for automation
    # pandas # if you process dataframes
    ```
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

Once installed and your virtual environment is active, you can run the assistant.

**IMPORTANT:** Always run ALPHA from a **standalone terminal** (like Windows Terminal, Command Prompt, or PowerShell on Windows; or your default terminal on Linux/macOS), NOT from an IDE's built-in output console (e.g., PyCharm's Run window), as `rich`'s interactive features require a true terminal environment.

```bash
python main_assistant.py # Or whatever your main script is named (e.g., app.py)
