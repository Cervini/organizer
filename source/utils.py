import os
import sys
import shutil
from typing import Optional
try:
    import winreg
except ImportError:
    winreg = None
import yaml
import threading
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("OrganizerLogger")

config_lock = threading.RLock()

def root_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)

def appdata_path():
    """Returns the path to the user's AppData/Roaming directory."""
    if sys.platform == "win32":
        return os.getenv('APPDATA')
    else:
        return os.path.join(os.path.expanduser('~'), '.organizer')

def setup_logging():
    """Sets up a rotating log file in the AppData directory."""
    appdata = appdata_path()
    log_dir = os.path.join(appdata, "Organizer")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "organizer.log")

    # Create a logger
    logger = logging.getLogger("OrganizerLogger")
    logger.setLevel(logging.INFO)

    # Create a rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

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
            logger.exception(f"Error occurred while reading the registry: {e}")
            return None
    else: # macOS and Linux
        return os.path.join(os.path.expanduser('~'), 'Downloads')
    
def filter_file_name(path) -> str:
    """Given a path returns only the file name"""
    name = path.split("/")
    return name[-1]

def load_config():
    """Returns the content of config.yaml"""
    # get the directory where the script is located
    config_file = root_path(os.path.join('resources', 'config.yaml'))

    if not os.path.exists(config_file):
        logger.error(f"'{config_file}' not found. Please create it.")
        return None
    with open(config_file, "r") as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            return None

def get_rules():
    """Returns just the rules from the config."""
    config = load_config()
    if config and "rules" in config and isinstance(config["rules"], list):
        return config["rules"]
    else:
        logger.error(f"Error: config.yaml is missing the 'rules' list.")
        return None

def get_interval():
    """Returns the sorting interval in minutes from the config."""
    config = load_config()
    return config.get("interval", 5) if config else 5

def save_interval(interval_minutes):
    """Saves the sorting interval to the config.yaml file."""
    if interval_minutes <= 0:
        interval_minutes = 5
    with config_lock:
        # Reload the config inside the lock to get the latest version
        config = load_config()
        if config is None:
            config = {'rules': [], 'interval': 5}
        config["interval"] = interval_minutes
        # The save_config function will handle the file writing safely
        save_config(config)
        logger.info("Interval updated in config.yaml")

def save_config(config):
    """Save the config to the config.yaml file."""
    config_file = root_path("resources/config.yaml")
    with config_lock:
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

def update_rule(updated_rule):
    """Update an existing rule in the config."""
    with config_lock:
        config = load_config()
        if config is not None:
            rules = config.get("rules", [])
            for i, rule in enumerate(rules):
                if rule.get("name") == updated_rule.get("name"):
                    rules[i] = updated_rule
                    config["rules"] = rules
                    save_config(config)
                    logger.info(f"{rule.get("name")} rule updated")
                    return True
    return False

def delete_rule_from_config(rule_name):
    """Delete a rule from the config by its name."""
    with config_lock:
        config = load_config()
        if config is not None:
            rules = config.get("rules", [])
            original_len = len(rules)
            rules = [rule for rule in rules if rule.get("name") != rule_name]
            if len(rules) < original_len:
                config["rules"] = rules
                save_config(config)
                logger.info(f"{rule_name} rule deleted")
                return True
    return False

def add_rule(new_rule):
    """Appends a new rule to the config."""
    with config_lock:
        config = load_config()
        if new_rule.get("sub"):
            create_folder(new_rule.get("destination"))
        if config is not None:
            rules = config.get("rules", [])
            rules.append(new_rule)
            config["rules"] = rules
            save_config(config)
            logger.info(f"Added {new_rule} rule to config.yaml")

def filter_file_name(path) -> str:
    """Returns the name of a file given the path"""
    name = path.split(f"\\")
    return name[-1]

def file_sorter():
    """Reads all the files in the default Download directory and moves them following the rulers in config.yaml"""
    # locate Download directory
    downloads_dir = locate_folder_path()

    # load sorting rules
    rules = get_rules()

    if not rules:
        return
    # scan folder and check files 
    try:
        for filename in os.listdir(downloads_dir):
            # build file path
            file_path = os.path.join(downloads_dir, filename)
            
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
                        destination_folder = os.path.join(downloads_dir, rule["destination"])
                    else:
                        destination_folder = rule["destination"]
                    # check if destination folder exists
                    if not os.path.isdir(destination_folder):
                        continue
                    
                    file_path = get_final_name(file_path, file_name, file_extension, destination_folder)

                    # Move the file
                    try:
                        shutil.move(file_path, destination_folder)
                        logger.info(f"Moved {filter_file_name(file_path)} to {destination_folder}.")
                        break # Stop checking rules for this file
                    except Exception as e:
                        logger.exception(f"Error moving {file_path}.")
                        break
    except PermissionError:
        logger.error("Permission denied accessing downloads folder")
    except Exception as e:
        logger.exception("Unexpected error in file_sorter")

def get_final_name(file_path, file_name, file_extension, destination_folder) -> str:
    """Renames the file if there is already a file with the same name in the destination folder"""
    count = 1
    new_name = file_name
    while os.path.isfile(os.path.join(destination_folder,filter_file_name(new_name)+file_extension)):
        # rename the new file
        new_name = file_name+"("+str(count)+")"
        os.rename(file_path, new_name+file_extension)
        # update file path
        file_path = new_name+file_extension
        count += 1
    
    return file_path

def create_folder(new_path):
    """Create folder in the Download folder"""
    downloads_dir = locate_folder_path()
    directory = os.path.join(downloads_dir, new_path)
    try:
        # Create the entire path.
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory '{directory}' is ready.")
    except Exception as e:
        logger.exception(f"An error occurred while trying to create directory '{directory}'.")

def create_folders():
    """Create the deafult folders named in the default config.yaml"""
    types = ["Images", "Documents", "Installers", "Archives"]

    for type in types:
        create_folder(type)