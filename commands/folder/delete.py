import os
import shutil
from google.genai import types

delete_folders_schema_dict = {
    "name": "delete_folders",
    "description": "Deletes one or more existing folders in known user directories.",
    "parameters": {
        "type": "object",
        "properties": {
            "folders_to_delete": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "folder_name": {
                            "type": "string",
                            "description": "Name of the folder to delete."
                        },
                        "location": {
                            "type": "string",
                            "description": "Location where the folder is (e.g., 'Desktop', 'Documents')."
                        }
                    },
                    "required": ["folder_name", "location"]
                },
                "description": "An array of folder objects to delete, each with 'folder_name' and 'location'."
            }
        },
        "required": ["folders_to_delete"]
    }
}

delete_folders_tool_schema = types.FunctionDeclaration(**delete_folders_schema_dict)

# Actual delete folders logic (accepts array)
def delete_folders(folders_to_delete: list) -> list:
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}
    results = []

    for folder_info in folders_to_delete:
        folder_name = folder_info.get("folder_name")
        location = folder_info.get("location")

        if not folder_name or not location:
            results.append(f"⚠️ Incomplete folder information: {folder_info}")
            continue

        if location not in valid_locations:
            results.append(f"❌ Invalid location '{location}' for '{folder_name}'. Choose from: {', '.join(valid_locations)}")
            continue

        folder_path = os.path.join(base_user_path, location, folder_name)

        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)  # Remove folder and its contents
                results.append(f"✅ Folder '{folder_name}' deleted from {location}.")
            else:
                results.append(f"❌ Folder '{folder_name}' does not exist at {location}.")
        except Exception as e:
            results.append(f"❌ Failed to delete folder '{folder_name}': {e}")

    return results