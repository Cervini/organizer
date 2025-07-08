import os
import sys
import shutil
from typing import Optional
import winreg
import yaml
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("OrganizerLogger")

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
        # For macOS and Linux, a common practice is to use a hidden folder in the home directory.
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
    else:
        logger.error(f"Unsupported OS")
        return None
    
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
    config = load_config()
    if config is None:
        config = {'rules': [], 'interval': 5}
    config["interval"] = interval_minutes
    config_file = root_path("resources/config.yaml")
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
        logger.info("Interval updated in config.yaml")

def save_config(config):
    """Save the config to the config.yaml file."""
    config_file = root_path("resources/config.yaml")
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

def update_rule(updated_rule):
    """Update an existing rule in the config."""
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
    config = load_config()
    if config is not None:
        rules = config.get("rules", [])
        rules.append(new_rule)
        config["rules"] = rules
        save_config(config)
        logger.info(f"Added {new_rule} rule to config.yaml")

def file_sorter():
    """Reads all the files in the default Download directory and moves them following the rulers in config.yaml"""
    # locate Download directory
    downloads_dir = locate_folder_path()

    # load sorting rules
    rules = get_rules()

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
                    logger.info(f"File with name {filter_file_name(new_name)+file_extension} already exists in target directory, renaming.")
                    new_name = file_name+"("+str(count)+")"
                    os.rename(file_path, new_name+file_extension)
                    # update file path
                    file_path = new_name+file_extension
                    count += 1
                
                # Move the file
                try:
                    shutil.move(file_path, destination_folder)
                    logger.info(f"Moved {filter_file_name(file_path)} to {destination_folder}.")
                    break # Stop checking rules for this file
                except Exception as e:
                    logger.exception(f"Error moving {file_path}.")
                    break
       
def create_folders():
    """Create the deafult folders named in the default config.yaml"""
    # locate Download directory
    downloads_dir = locate_folder_path()

    types = ["Images", "Documents", "Installers", "Archives"]

    for type in types:
        directory = downloads_dir + '/' + type
        try:
            os.mkdir(directory)
            logger.info(f"{type} directory created.")
        except FileExistsError:
            logger.warning(f"Couldn't create {type} directory because it already existed.")
            continue # if the directory already exists do nothing
        except Exception as e:
            logger.exception(f"An error occurred while trying to create {type} directory.")