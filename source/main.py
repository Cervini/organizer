import time
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image
import utils
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    return os.path.join(base_path, relative_path)

stop_event = threading.Event()

# organize files after 5 minutes loop
def organize_files_loop():
    """ Run file sorter every 5 minutes"""
    while not stop_event.is_set():
        utils.file_sorter()
        for _ in range(300):
            if stop_event.is_set():
                break
            # waiting 1 second at a times allows to promptly stop the loop
            time.sleep(1)

def exit_action(icon, item):
    stop_event.set()
    icon.stop()

def main():
    # Use the robust function to find the image in the resources folder
    image_path = resource_path("resources/broom.png")

    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        # if not found, create placeholder
        image = Image.new('RGB', (64, 64), 'black')

    # link 'Exit' menu item to 'exit_action' function
    menu = (item('Exit', exit_action),)

    # create icon instance
    icon = pystray.Icon("Project Organizer", image, "Project Organizer", menu)

    # Create and start background thread for organization logic
    organization_thread = threading.Thread(target=organize_files_loop)
    organization_thread.daemon = True # Allows main program to exit even if thread is running
    organization_thread.start()

    # run system tray icon
    icon.run()

if __name__ == "__main__":
    main()