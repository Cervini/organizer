import time
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image
import utils
import gui

stop_event = threading.Event()

# -- Core application logic --
def organize_files_loop():
    """ Run file sorter every set amount of time read from config file"""
    while not stop_event.is_set():
        utils.file_sorter()
        interval = utils.get_interval()*60
        for _ in range(interval*60):
            if stop_event.is_set():
                break
            if utils.get_interval()*60 != interval:
                utils.logger.info(f"Time interval updated, set to {utils.get_interval()}.")
                break
            # waiting 1 second at a times allows to promptly stop the loop
            time.sleep(1)

def exit_action(icon, item):
    stop_event.set()
    icon.stop()

# -- Main --
def main():
    utils.setup_logging()

    # Use the robust function to find the image in the resources folder
    image_path = utils.root_path("resources/broom.png")

    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        # if not found, create placeholder
        utils.logger.warning(f"Icon file not found at {image_path}. Using placeholder.")
        image = Image.new('RGB', (64, 64), 'black')

    # link menu items to functions
    menu = (item('Configure Rules', gui.open_config_window_threaded), item('Exit', exit_action),)

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