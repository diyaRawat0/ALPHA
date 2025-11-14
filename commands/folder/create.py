import os

def create_folder(location: str, folder_names: list):
    """Creates multiple folders in the specified location."""

    user_home = os.path.expanduser("~")
    target_path = os.path.join(user_home, location)
    created_folders = []

    if not os.path.isdir(target_path):
        return f"Error: Location '{location}' not found under user directory."

    for folder_name in folder_names:
        new_folder_path = os.path.join(target_path, folder_name)
        try:
            os.makedirs(new_folder_path, exist_ok=True)
            created_folders.append(new_folder_path)
        except Exception as e:
            return f"Error creating folder '{folder_name}': {e}"
    return {"created": created_folders}


create_folder_schema_dict = {
    "name": "create_folder",
    "description": "Creates one or more folders inside a known user directory like Desktop or Documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "Target location under the user directory (e.g., 'Desktop', 'Documents')."
            },
            "folder_names": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "Name of a folder to create."
                },
                "description": "An array of folder names to create."
            }
        },
        "required": ["location", "folder_names"]
    }
}