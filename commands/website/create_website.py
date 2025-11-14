# commands/website/create_website.py
import os
import json
import webbrowser
from commands.website.open_website import open_website
from google.genai import types

# --- Configuration ---
BASE_WEBSITE_DIR = os.path.join(os.path.expanduser("~"), "Websites")
os.makedirs(BASE_WEBSITE_DIR, exist_ok=True) # Ensure base directory exists

# --- MODIFIED FUNCTION: folder_path parameter removed ---
def create_website(website_name: str = None, content: str = None) -> dict:
    if website_name is None:
        return {"success": False, "message": "Website name is required.", "path": None}

    # --- SIMPLIFIED LOGIC: Always use BASE_WEBSITE_DIR ---
    actual_folder_path = BASE_WEBSITE_DIR
    # --- END SIMPLIFIED LOGIC ---

    full_path = os.path.join(actual_folder_path, website_name)
    index_html_path = os.path.join(full_path, "index.html")

    creation_result = {}
    open_result = {}

    try:
        os.makedirs(full_path, exist_ok=True)
        print(f"Created directory: {full_path}")

        if content is None:
            content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{website_name.replace('_', ' ').title()}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body class="bg-gradient-to-r from-blue-500 to-purple-600 min-h-screen flex items-center justify-center text-white p-4">
    <div class="bg-white bg-opacity-20 backdrop-filter backdrop-blur-lg rounded-xl shadow-2xl p-8 md:p-12 text-center max-w-2xl w-full border border-white border-opacity-30">
        <h1 class="text-4xl md:text-5xl font-extrabold mb-4 animate-bounce">
            Welcome to <span class="text-yellow-300">{website_name.replace('_', ' ').title()}</span>!
        </h1>
        <p class="text-lg md:text-xl mb-6">
            This is a simple website created using model function calling.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
            <a href="#" class="bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold py-3 px-6 rounded-lg shadow-lg transform transition duration-300 hover:scale-105">
                Learn More
            </a>
            <a href="#" class="bg-green-400 hover:bg-green-500 text-gray-900 font-bold py-3 px-6 rounded-lg shadow-lg transform transition duration-300 hover:scale-105">
                Get Started
            </a>
        </div>
        <p class="mt-8 text-sm opacity-80">
            &copy; {website_name.replace('_', ' ').title()} {os.path.basename(os.path.dirname(os.path.abspath(__file__)))}
        </p>
    </div>
</body>
</html>
            """

        with open(index_html_path, "w") as f:
            f.write(content)
        print(f"Created index.html at: {index_html_path}")
        creation_result = {"success": True, "message": f"Website '{website_name}' created successfully at {full_path}", "path": index_html_path}

        print(f"Attempting to open website: {index_html_path}")
        open_result = open_website(index_html_path=index_html_path)
        print(f"Website open attempt result: {open_result}")

    except Exception as e:
        creation_result = {"success": False, "message": f"Error creating website: {e}", "path": None}
        open_result = {"success": False, "message": f"Website not opened due to creation error: {e}"}

    combined_result = {
        "website_creation": creation_result,
        "website_opening": open_result
    }
    return combined_result

# --- MODIFIED SCHEMA: folder_path parameter removed ---
create_website_schema_dict = types.FunctionDeclaration(
    name="create_website",
    description="Creates a new folder and an index.html file inside it for a website in the default 'Websites' folder in your user directory, and automatically opens it.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "website_name": types.Schema(
                type=types.Type.STRING,
                description="The desired name for the website folder (e.g., 'my_new_blog', 'company_landing_page')."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Optional HTML content for the index.html file. If not provided, a default template will be used. This parameter is typically filled by model's generation based on user's prompt."
            )
        },
        required=["website_name"]
    )
)