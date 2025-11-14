from commands.folder.create import create_folder
from commands.folder.delete import delete_folders
from commands.folder.move import move_folders
from commands.folder.rename import rename_folders
from commands.files.create_python_file import create_python_file
from commands.website.create_website import create_website
from commands.website.open_website import open_website
from commands.webautomation.youtube_Automation import open_youtube_trending
from commands.webautomation.web_scrapper import scrape_website_content
from commands.webautomation.gehu_Automation import open_gehu_btech_notice_and_return_content
executable_functions = {
    "create_folder": create_folder,
    "delete_folders": delete_folders,
    "move_folders": move_folders,
    "rename_folders": rename_folders,
    "create_python_file": create_python_file,
    "create_website": create_website,
    "open_website": open_website,
    "open_youtube_trending": open_youtube_trending,
    "scrape_website_content": scrape_website_content,
    "open_gehu_btech_notice_and_return_content": open_gehu_btech_notice_and_return_content
}
