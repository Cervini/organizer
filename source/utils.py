import os
import sys
import shutil
from typing import Optional
from pathlib import Path
import winreg
import yaml

def root_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)

def locate_folder_path() -> Optional[str]:
    """ Returns Downloads folder path """
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
    """ Given a path returns only the file name """
    name = path.split("/")
    return name[-1]

def load_config():

    # get the directory where the script is located
    script_dir = Path(__file__).resolve().parent
    
    # build the full, absolute path to the config file
    config_file = script_dir / "config.yaml"

    if not os.path.exists(config_file):
        print(f"Error: '{config_file}' not found. Please create it.")
        return None
    with open(config_file, "r") as f:
        try:
            config = yaml.safe_load(f)
            if "rules" in config and isinstance(config["rules"], list):
                return config["rules"]
            else:
                print(f"Error: '{config_file}' is missing the 'rules' list.")
                return None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return None

def save_config(rules):
    """Save the rules to the config.yaml file."""
    config_file = root_path("source/config.yaml")
    with open(config_file, "w") as f:
        yaml.dump({"rules": rules}, f, default_flow_style=False)

def update_rule(updated_rule):
    """Update an existing rule in the config."""
    rules = load_config()
    if rules is not None:
        for i, rule in enumerate(rules):
            if rule.get("name") == updated_rule.get("name"):
                rules[i] = updated_rule
                save_config(rules)
                return True
    return False


def delete_rule_from_config(rule_name):
    """Delete a rule from the config by its name."""
    rules = load_config()
    if rules is not None:
        original_len = len(rules)
        rules = [rule for rule in rules if rule.get("name") != rule_name]
        if len(rules) < original_len:
            save_config(rules)
            return True
    return False

def file_sorter():

    # locate Download directory
    downloads_dir = locate_folder_path()

    # load sorting rules
    rules = load_config()

    if not rules:
        return
    # scan folder and check files 

    # os.listdir() gives a list of every sub-directory and file name
    for filename in os.listdir(downloads_dir):
        # build file path
        file_path = downloads_dir + '/' + filename
        
        # check if file
        if not os.path.isfile(file_path):
            continue
    
        # get file name and extension
        file_name, file_extension = os.path.splitext(file_path)

        # Check against each rule
        for rule in rules:

            # Check if the file extension matches
            match_extension = file_extension in rule.get("extensions", [])
            
            # Check if any keyword matches
            match_keyword = False
            if rule.get("keywords"):
                match_keyword = any(keyword.lower() in file_name for keyword in rule["keywords"])

            if match_extension or match_keyword:

                # check if destination is sub-folder
                if rule["sub"]:
                    destination_folder = downloads_dir + "/" + rule["destination"]
                else:
                    destination_folder = rule["destination"]

                # check if destination folder exists
                if not os.path.isdir(destination_folder):
                    continue
                
                # check if there is already a file with the same name in destination folder
                count = 1
                new_name = file_name
                while os.path.isfile(destination_folder+"/"+filter_file_name(new_name)+file_extension):
                    # rename the new file
                    new_name = file_name+"("+str(count)+")"
                    os.rename(file_path, new_name+file_extension)
                    # update file path
                    file_path = new_name+file_extension
                    count += 1
                
                # Move the file
                try:
                    shutil.move(file_path, destination_folder)
                    break # Stop checking rules for this file
                except Exception as e:
                    print(f"Error moving {file_path}: {e}")
                    break