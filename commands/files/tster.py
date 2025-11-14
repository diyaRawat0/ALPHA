from google import genai
import requests
import json
import os
# --- Configuration for your Gemini project backend ---
# Replace with your actual Gemini API key
# Ensure you have your Gemini API key set up as an environment variable
# or replace "YOUR_GEMINI_API_KEY" with your actual key.
# For security, it's best to use environment variables.

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = client.chats.create(model="gemini-2.0-flash")

# --- Local Flask Server Configuration (from simple-website-creator.py) ---
LOCAL_API_BASE_URL = "http://127.0.0.1:5000"

# --- Tool Definitions for Gemini ---
# These are the same tool definitions you'd pass to Gemini.
# Note: The 'content' parameter for create_website is now optional
# because Gemini will generate it if not explicitly provided by the user.

create_website_tool_definition = {
    "name": "create_website",
    "description": "Creates a new folder and an index.html file inside it for a website.",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "The absolute path where the new website folder should be created (e.g., 'C:/Users/YourUser/Documents/MySites'). Defaults to a 'GeminiWebsites' folder in your user directory if not provided."
            },
            "website_name": {
                "type": "string",
                "description": "The desired name for the website folder (e.g., 'my_new_blog', 'company_landing_page')."
            },
            "content": {
                "type": "string",
                "description": "Optional HTML content for the index.html file. If not provided, a default template will be used. This parameter is typically filled by Gemini's generation."
            }
        },
        "required": ["website_name"]
    }
}

open_website_tool_definition = {
    "name": "open_website",
    "description": "Opens the specified index.html file in the default web browser.",
    "parameters": {
        "type": "object",
        "properties": {
            "index_html_path": {
                "type": "string",
                "description": "The absolute path to the index.html file to open."
            }
        },
        "required": ["index_html_path"]
    }
}

# --- Main Logic for Handling User Prompt and Gemini Interaction ---

def handle_user_request(user_prompt: str):
    """
    Processes a user's request, potentially generating website content and
    calling local tools.
    """
    print(f"User prompt received: '{user_prompt}'")

    # Step 1: Ask Gemini to generate content or suggest a tool call
    # We instruct Gemini to use the 'create_website' tool and to generate the 'content'
    # based on the user's prompt.
    # The prompt should be structured to guide Gemini to produce HTML.
    system_instruction = (
        "You are a helpful assistant that can create simple websites. "
        "When asked to create a website, use the `create_website` tool. "
        "Generate the full HTML content for the website, including `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` tags. "
        "Ensure the HTML is well-formed and includes basic styling if appropriate (e.g., using Tailwind CSS from CDN). "
        "If the user specifies a website name or folder, use those parameters in the tool call. "
        "If the user asks to open a website, use the `open_website` tool."
    )

    # Example of how to structure the prompt to encourage tool use and content generation
    # We add a specific instruction for content generation within the prompt itself.
    full_prompt = f"{system_instruction}\n\nUser: {user_prompt}\n\n" \
                  f"Please generate the HTML content for the website and then call the `create_website` tool with the generated content."

    try:
        response = model.generate_content(
            full_prompt,
            tools=[create_website_tool_definition, open_website_tool_definition]
        )

        # Step 2: Process Gemini's response
        if response.candidates:
            candidate = response.candidates[0]
            if candidate.tool_calls:
                for tool_call in candidate.tool_calls:
                    function_name = tool_call.function.name
                    function_args = tool_call.function.args
                    print(f"Gemini suggested tool call: {function_name} with args: {function_args}")

                    if function_name == "create_website":
                        # Ensure 'content' is present, if not, Gemini might have missed it
                        # or the user's prompt didn't imply content generation.
                        # For this scenario, we expect Gemini to provide content.
                        if 'content' not in function_args or not function_args['content']:
                            print("Warning: Gemini did not provide content for create_website. Attempting to generate default content.")
                            # Fallback: If Gemini didn't provide content, you could try to generate it here
                            # or use a default. For this example, we'll assume Gemini *should* provide it.
                            # If you want Gemini to *always* generate, you might need a more specific prompt.
                            # For now, let's assume Gemini generates it.
                            pass # We'll rely on Gemini to put content in function_args

                        # Call your local Flask server
                        try:
                            local_response = requests.post(
                                f"{LOCAL_API_BASE_URL}/create_website",
                                json=function_args
                            )
                            local_response.raise_for_status() # Raise an exception for HTTP errors
                            result = local_response.json()
                            print(f"Local server response: {result}")

                            if result['success']:
                                print(f"Website created: {result['message']}")
                                # Store the index_html_path for potential future 'open_website' calls
                                return f"Website created successfully: {result['message']}. You can now ask me to open it by saying 'open the website at {result['index_html_path']}'"
                            else:
                                return f"Failed to create website: {result['message']}"
                        except requests.exceptions.RequestException as e:
                            return f"Error communicating with local server for create_website: {e}. Is your `simple-website-creator.py` script running?"

                    elif function_name == "open_website":
                        try:
                            local_response = requests.post(
                                f"{LOCAL_API_BASE_URL}/open_website",
                                json=function_args
                            )
                            local_response.raise_for_status()
                            result = local_response.json()
                            print(f"Local server response: {result}")

                            if result['success']:
                                return f"Website opened: {result['message']}"
                            else:
                                return f"Failed to open website: {result['message']}"
                        except requests.exceptions.RequestException as e:
                            return f"Error communicating with local server for open_website: {e}. Is your `simple-website-creator.py` script running?"
                    else:
                        return f"Gemini suggested an unknown tool: {function_name}"
            elif candidate.content and candidate.content.parts:
                # If Gemini just generated text and no tool call, handle it as a normal response
                generated_text = candidate.content.parts[0].text
                print(f"Gemini generated text: {generated_text}")
                return generated_text
            else:
                return "Gemini did not provide a tool call or text content."
        else:
            return "No response from Gemini."

    except genai.types.BlockedPromptException as e:
        return f"Gemini prompt was blocked: {e}"
    except Exception as e:
        return f"An unexpected error occurred during Gemini interaction: {e}"

# --- Example Usage (simulating a user interaction) ---
if __name__ == '__main__':
    print("--- Simulating Gemini Backend Interaction ---")
    print("Make sure your `simple-website-creator.py` script is running in another terminal.")
    print("Try prompts like:")
    print("- 'create a website named my_first_page that says Hello, World!'")
    print("- 'make a simple webpage about cats'")
    print("- 'open the website at C:/Users/YourUser/GeminiWebsites/my_first_page/index.html' (adjust path)")

    while True:
        user_input = input("\nEnter your request (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        response_message = handle_user_request(user_input)
        print(f"\nAssistant: {response_message}")

