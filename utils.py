import os
import sys
import shutil
from typing import Optional
import winreg

def locate_folder_path() -> Optional[str]:
    if sys.platform == "win32": # Windows
        try:
            # Open the registry key that stores user shell folder paths
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                # The GUID for the Downloads folder is {374DE290-123F-4565-9164-39C4925E467B}
                downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
                path_str, _ = winreg.QueryValueEx(key, downloads_guid)
                return os.path.expandvars(path_str)
        except FileNotFoundError:
            # Fallback in case the registry key is not found
            return os.path.join(os.path.expanduser('~'), 'Downloads')
        except Exception as e:
            print(f"Error occurred while reading the registry: {e}")
            return None
    else:
        print("Unsupported OS")
        return None
    
def filter_file_name(path) -> str:
    name = path.split("/")
    return name[-1]

def file_sorter():
    
    # Locate Download directory
    downloads_dir = locate_folder_path()

    # Scan folder and check files 

    # os.listdir() gives a list of every sub-directory and file name
    for filename in os.listdir(downloads_dir):
        # build file path
        file_path = downloads_dir + '/' + filename
        
        # check if file
        if os.path.isfile(file_path):
            # get file name
            # get extention
            file_name, file_extension = os.path.splitext(file_path)
            # sort from name
            if "token" in file_name:
                shutil.move(file_path, r"D:\Documents\D&D\Tokens")
            # sort from exptension
            elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                shutil.move(file_path, downloads_dir+'/'+"img/")
            elif file_extension in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt']:
                shutil.move(file_path, downloads_dir+'/'+"docs/")
            elif file_extension in ['.zip', '.rar', '.7z', '.gz']:
                shutil.move(file_path, downloads_dir+'/'+"archives/")
            elif file_extension in ['.exe', '.msi']:
                shutil.move(file_path, downloads_dir+'/'+"installers/")
            else:
                # extension not classified
                shutil.move(file_path, downloads_dir+'/'+"others/")