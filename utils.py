import os
import sys
import pathlib
from typing import Optional

# Conditional import for the winreg module on Windows
if sys.platform == "win32":
    import winreg

def locate_folder_path() -> Optional[str]:
    """
    Finds the default Downloads folder path on the current operating system.
    """
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
            
    elif sys.platform == "darwin":  # macOS
        return os.path.join(os.path.expanduser('~'), 'Downloads')
        
    elif sys.platform.startswith("linux"): # Linux
        try:
            home = os.path.expanduser("~")
            config = os.path.join(home, ".config/user-dirs.dirs")
            if os.path.exists(config):
                with open(config, 'r') as f:
                    for line in f:
                        if line.startswith("XDG_DOWNLOAD_DIR"):
                            path = line.split('"')[1]
                            return path.replace("$HOME", home)
        except Exception:
            return os.path.join(os.path.expanduser('~'), 'Downloads')

    else:
        print("Unsupported OS")
        return None
    
def filter_file_name(path) -> str:
    name = path.split("/")
    return name[-1]

if __name__ == "__main__":
    downloads_folder = locate_folder_path()
    if downloads_folder:
        print(f"The Downloads folder is located at: {downloads_folder}")
    else:
        print("Could not determine the Downloads folder path.")