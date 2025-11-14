import os
import shutil
from google.genai import types

# Function schema for Gemini (accepts array of folders to move)
move_folders_schema_dict = {
    "name": "move_folders",
    "description": "Moves one or more folders from their source locations to a single target location within known user directories.",
    "parameters": {
        "type": "object",
        "properties": {
            "folders_to_move": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "folder_name": {
                            "type": "string",
                            "description": "Name of the folder to move."
                        },
                        "source_location": {
                            "type": "string",
                            "description": "Current location where the folder is (e.g., 'Desktop', 'Documents')."
                        }
                    },
                    "required": ["folder_name", "source_location"]
                },
                "description": "An array of folder objects to move, each with 'folder_name' and 'source_location'."
            },
            "target_location": {
                "type": "string",
                "description": "Destination location for all specified folders (e.g., 'Desktop', 'Documents')."
            }
        },
        "required": ["folders_to_move", "target_location"]
    }
}

move_folders_tool_schema = types.FunctionDeclaration(**move_folders_schema_dict)

# Actual move folders logic (accepts array)
def move_folders(folders_to_move: list, target_location: str) -> list:
    base_user_path = r"C:\Users\aryav"
    valid_locations = {"Desktop", "Documents", "Downloads", "Pictures"}
    results = []

    if target_location not in valid_locations:
        return [f"❌ Invalid target location '{target_location}'. Choose from: {', '.join(valid_locations)}"]

    for folder_info in folders_to_move:
        folder_name = folder_info.get("folder_name")
        source_location = folder_info.get("source_location")

        if not folder_name or not source_location:
            results.append(f"⚠️ Incomplete folder information: {folder_info}")
            continue

        if source_location not in valid_locations:
            results.append(f"❌ Invalid source location '{source_location}' for '{folder_name}'. Choose from: {', '.join(valid_locations)}")
            continue

        source_folder_path = os.path.join(base_user_path, source_location, folder_name)
        target_folder_path = os.path.join(base_user_path, target_location, folder_name)

        try:
            if os.path.exists(source_folder_path):
                shutil.move(source_folder_path, target_folder_path)
                results.append(f"✅ Folder '{folder_name}' moved from {source_location} to {target_location}.")
            else:
                results.append(f"❌ Folder '{folder_name}' not found at {source_location}.")
        except Exception as e:
            results.append(f"❌ Failed to move folder '{folder_name}': {e}")

    return results