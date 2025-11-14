# backend/assistant_core.py
import json
import os
from google import genai
from google.genai import types
from google.generativeai.types import Tool, FunctionDeclaration

# Assuming these imports are correct and available in your environment
from core.function_router import route_function_call
from commands.folder.create import create_folder_schema_dict
from commands.folder.delete import delete_folders_schema_dict
from commands.folder.move import move_folders_schema_dict
from commands.folder.rename import rename_folders_schema_dict
from commands.files.create_python_file import create_python_file_schema_dict
from commands.website.create_website import create_website_schema_dict
from commands.website.open_website import open_website_schema_dict
from commands.webautomation.youtube_Automation import open_youtube_trending_schema_dict
from commands.webautomation.web_scrapper import scrape_website_content_schema_dict
from commands.webautomation.gehu_Automation import open_gehu_btech_notice_and_return_content_schema_dict


class GeminiAssistant:
    def __init__(self):
        # Ensure GEMINI_API_KEY is loaded from environment variables
        # It's good practice to load dotenv at the application's entry point,
        # but if this class is directly instantiated, you might need it here too.
        # from dotenv import load_dotenv
        # load_dotenv()

        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # Initialize the chat session. This will store the conversation history.
        # It's generally better to use a model that supports multi-turn conversations directly.
        # For non-streaming, `generate_content` is also an option if you manage history manually.
        # However, `client.chats.create` and `chat.send_message` are designed for turn-based conversations.
        self.chat = self.client.chats.create(model="gemini-2.0-flash")

        self.route_function_call = route_function_call

        # Define tools for function calling
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
                             open_gehu_btech_notice_and_return_content_schema_dict, ]
                            )]
        self.config = {
            "tools": tools,
            # If you want to force the model to explicitly call functions,
            # you can set `automatic_function_calling` to `{"disable": True}` as you have.
            # If you want the model to call functions automatically, remove this line or set to {"disable": False}.
            "automatic_function_calling": {"disable": True}
        }

    def handle_website_creation_follow_up(self, created_website_path: str) -> types.Part:
        # This function seems to involve user input, which is blocking for a GUI application.
        # In a GUI context, you'd typically emit a signal to the GUI to ask the user,
        # and then a slot in the GUI would trigger the next action.
        # For now, I'm keeping it as is, but be aware this `input()` will block your UI.
        print("\nAssistant: Website created successfully. Do you want to open it now? (yes/no)")
        user_wants_to_open = input("Your choice: ").strip().lower()

        if user_wants_to_open == 'yes' or user_wants_to_open == 'y':
            open_website_call_object = types.FunctionCall(
                name='open_website',
                args={'index_html_path': created_website_path}
            )
            function_result = self.route_function_call(open_website_call_object)
            return types.Part.from_function_result(
                name='open_website',
                response=json.dumps(function_result)
            )
        else:
            return None

    def send_prompt(self, prompt: str):
        """
        Sends a prompt to the Gemini model and returns the complete text response
        or handles a function call.
        """
        try:
            # Use send_message for non-streaming. This sends the prompt
            # and automatically appends it to the chat history.
            response = self.chat.send_message(prompt, config=self.config)

            # Check if the response contains a function call
            if response.candidates and response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                if part.function_call:
                    tool_call_object = part.function_call
                    function_result = self.route_function_call(tool_call_object)

                    # Send the function result back to the model as a new message
                    # This completes the turn for the model to generate a text response
                    response_from_tool_result = self.chat.send_message(
                        "Function Result: " + str(function_result) + " So, draft a small confirming message."
                    )

                    if response_from_tool_result.text:
                        # Return the model's text response after the function call
                        yield "final_text", response_from_tool_result.text
                    else:
                        yield "final_text", "Operation completed."
                elif part.text:
                    # If it's a text response, return it directly
                    yield "final_text", part.text
                else:
                    # Fallback for unexpected part types
                    yield "error", "No valid content (text or function_call) received from the model."
            else:
                yield "error", "No candidates or content parts in the model's response."

        except Exception as e:
            # Catch any exceptions during the API call or processing
            yield "error", f"An error occurred during prompt processing: {e}"