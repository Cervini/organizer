import time
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image
import utils
import sys
import os
import tkinter as tk
from tkinter import scrolledtext

def root_path(relative_path):
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

def open_config_window_threaded():
    # Run the window in its own thread
    config_thread = threading.Thread(target=open_config_window)
    config_thread.daemon = True
    config_thread.start()

def open_config_window():
    config_window = tk.Tk()
    config_window.title("Configure Rules")
    config_window.resizable(True, True)
    
    # Add a Text widget to display the rules
    text_area = scrolledtext.ScrolledText(config_window, wrap=tk.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10, expand=True, fill='both')
    
    # Load and display the rules from config.yaml
    try:
        with open(root_path("source/config.yaml"), "r") as f:
            rules_text = f.read()
            text_area.insert(tk.INSERT, rules_text)
    except FileNotFoundError:
        text_area.insert(tk.INSERT, "Could not find config.yaml")
        
    config_window.mainloop()

def main():
    # Use the robust function to find the image in the resources folder
    image_path = root_path("resources/broom.png")

    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        # if not found, create placeholder
        image = Image.new('RGB', (64, 64), 'black')

    # link menu items to functions
    menu = (item('Configure Rules', open_config_window_threaded), item('Exit', exit_action),)

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