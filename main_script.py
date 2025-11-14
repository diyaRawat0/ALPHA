import os
import json
from google import genai
from google.genai import types
from core.function_router import route_function_call # This import remains for functionality
from google.generativeai.types import Tool, FunctionDeclaration # This import remains for functionality

from commands.folder.create import create_folder_schema_dict, create_folder
from commands.folder.delete import delete_folders_schema_dict, delete_folders
from commands.folder.move import move_folders_schema_dict, move_folders
from commands.folder.rename import rename_folders_schema_dict, rename_folders
from commands.files.create_python_file import create_python_file_schema_dict, create_python_file
from commands.website.create_website import create_website_schema_dict, create_website
from commands.website.open_website import open_website_schema_dict, open_website
from commands.webautomation.youtube_Automation import open_youtube_trending_schema_dict
from commands.webautomation.web_scrapper import scrape_website_content_schema_dict
from commands.webautomation.gehu_Automation import open_gehu_btech_notice_and_return_content_schema_dict

def display_welcome_message():
    """Displays a welcoming and informative message for the user."""
    print("--------------------------------------------------")
    print("🤖 AI Assistant Ready! 🤖")
    print("--------------------------------------------------")
    print("\nWelcome to your Model!")
    print("I am an AI assistant designed to help you automate various tasks.")
    print("Simply type your command or request at the prompt.")
    print("Type 'exit' to quit the conversation.")
    print("--------------------------------------------------")

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-2.0-flash")
    # No "Initialization successful!" message, as per request for minimal output
except Exception as e:
    print(f"Error initializing model: {e}")
    exit(1) # Exit if API fails to initialize

# --- Tool Configuration ---
tools = [types.Tool(function_declarations=
                    [create_folder_schema_dict,
                     delete_folders_schema_dict,
                     move_folders_schema_dict,
                     rename_folders_schema_dict,
                     create_python_file_schema_dict,
                     create_website_schema_dict,
                     open_website_schema_dict,
                     open_youtube_trending_schema_dict,
                     scrape_website_content_schema_dict,
                     open_gehu_btech_notice_and_return_content_schema_dict,]
                    )]
config = {
    "tools": tools,
    "automatic_function_calling": {"disable": True}
}

def handle_website_creation_follow_up(created_website_path: str) -> types.Part:
    print("\nAssistant: Website created successfully. Do you want to open it now? (yes/no)")
    user_wants_to_open = input("Your choice: ").strip().lower()

    if user_wants_to_open == 'yes' or user_wants_to_open == 'y':
        open_website_call_object = types.FunctionCall(
            name='open_website',
            args={'index_html_path': created_website_path}
        )
        function_result = route_function_call(open_website_call_object)
        return types.Part.from_function_result(
            name='open_website',
            response=json.dumps(function_result)
        )
    else:
        return None

display_welcome_message()

while True:
    user_prompt = input("Enter your prompt: ")
    if user_prompt.lower() == 'exit':
        break

    try:
        stream_response = chat.send_message_stream(user_prompt, config=config)

        collected_text = ""
        function_call_triggered = False
        tool_call_object = None

        for chunk in stream_response:
            if chunk.candidates and chunk.candidates[0].content.parts:
                part = chunk.candidates[0].content.parts[0]
                if part.text:
                    collected_text += part.text
                    print(part.text, end="") # Print text as it streams
                elif part.function_call and not function_call_triggered:
                    # Capture the first function call and set a flag
                    tool_call_object = part.function_call
                    function_call_triggered = True

                    break

        print()

        if function_call_triggered and tool_call_object:
            tool_name = tool_call_object.name

            function_result = route_function_call(tool_call_object)
            response_from_tool_result = chat.send_message("Function Result: " + str(function_result) + " So, draft a small confirming message.")

            if response_from_tool_result.text:
                print(f"Assistant: {response_from_tool_result.text}")
            else:
                print("Assistant: Operation completed.") # Generic confirmation
        elif collected_text:
            pass
        else:
            print("Error: No valid content received from the model.")

    except Exception as e:
        print(f"An error occurred: {e}")

print("\nExiting conversation.")