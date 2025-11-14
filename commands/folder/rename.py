import os
from google.genai import types

# Function schema for Gemini (accepts array of folders to rename)
rename_folders_schema_dict = {
    "name": "rename_folders",
    "description": "Renames one or more existing folders in known user directories.",
    "parameters": {
        "type": "object",
        "properties": {
            "folders_to_rename": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "old_folder_name": {
                            "type": "string",
                            "description": "Current name of the folder."
                        },
                        "new_folder_name": {
                            "type": "string",
                            "description": "New name for the folder."
                        },
                        "location": {
                            "type": "string",
                            "description": "Location where the folder is (e.g., 'Desktop', 'Documents')."
                        }
                    },
                    "required": ["old_folder_name", "new_folder_name", "location"]
                },
                "description": "An array of folder objects to rename, each with 'old_folder_name', 'new_folder_name', and 'location'."
            }
        },
        "required": ["folders_to_rename"]
    }
}

rename_folders_tool_schema = types.FunctionDeclaration(**rename_folders_schema_dict)

# Actual rename folders logic (accepts array)
def rename_folders(folders_to_rename: list) -> list:
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}
    results = []

    for folder_info in folders_to_rename:
        old_folder_name = folder_info.get("old_folder_name")
        new_folder_name = folder_info.get("new_folder_name")
        location = folder_info.get("location")

        if not old_folder_name or not new_folder_name or not location:
            results.append(f"⚠️ Incomplete folder information: {folder_info}")
            continue

        if location not in valid_locations:
            results.append(f"❌ Invalid location '{location}' for '{old_folder_name}'. Choose from: {', '.join(valid_locations)}")
            continue

        old_folder_path = os.path.join(base_user_path, location, old_folder_name)
        new_folder_path = os.path.join(base_user_path, location, new_folder_name)

        try:
            if os.path.exists(old_folder_path):
                os.rename(old_folder_path, new_folder_path)
                results.append(f"✅ Folder renamed from '{old_folder_name}' to '{new_folder_name}' at {location}.")
            else:
                results.append(f"❌ Folder '{old_folder_name}' not found at {location}.")
        except Exception as e:
            results.append(f"❌ Failed to rename folder '{old_folder_name}': {e}")

    return results
