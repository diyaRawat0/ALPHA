# commands/website/open_website.py
import os
import webbrowser
from google.genai import types

def open_website(index_html_path: str = None) -> dict:

    if index_html_path is None:
        return {"success": False, "message": "Path to index.html is required.", "path": None}

    if not os.path.exists(index_html_path):
        return {"success": False, "message": f"Error: File '{index_html_path}' does not exist.", "path": None}

    try:
        webbrowser.open(f"file:///{index_html_path.replace(os.sep, '/')}")
        print(f"Opened website: {index_html_path}")
        return {"success": True, "message": f"Website opened successfully in your default browser: {index_html_path}", "path": index_html_path}
    except Exception as e:
        return {"success": False, "message": f"Error opening website: {e}", "path": None}

open_website_schema_dict = types.FunctionDeclaration(
    name="open_website",
    description="Opens the specified index.html file in the default web browser.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "index_html_path": types.Schema(
                type=types.Type.STRING,
                description="The absolute path to the index.html file to open."
            )
        },
        required=["index_html_path"]
    )
)