import time
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image
import utils
import tkinter as tk
from tkinter import ttk

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

    # window settings
    config_window = tk.Tk()
    config_window.title("Configure Rules")
    w=600
    h=500
    ws=config_window.winfo_screenwidth()
    hs=config_window.winfo_screenheight()
    x=(ws/2)-(w/2)
    y=(hs/2)-(h/2)
    config_window.geometry('%dx%d+%d+%d'%(w,h,x,y))

    # masin frame
    main_frame = tk.Frame(config_window)
    main_frame.pack(fill='both', expand=True)
    
    # make window scrollable with mouse wheel
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # --- Bind canvas resizing to frame resizing ---
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", on_canvas_configure)
    # --- End resizing binding ---

    # --- Mouse wheel scrolling ---
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Bind the mousewheel event to the canvas
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    # --- End mouse wheel scrolling ---
    
    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")

    # Load rules and display them
    rules = utils.load_config()

    if rules:
        for _, rule in enumerate(rules):
            rule_frame = ttk.LabelFrame(scrollable_frame, text=f"{rule.get('name', 'N/A')}", padding="10")
            rule_frame.pack(pady=10, padx=10, fill="x", expand=True)
            
            # Extensions
            ttk.Label(rule_frame, text="Extensions:").grid(row=0, column=0, sticky="w", pady=2)
            ext_text = ", ".join(rule.get('extensions', [])) or "Any"
            ttk.Label(rule_frame, text=ext_text, wraplength=350).grid(row=0, column=1, sticky="w")
            
            # Keywords
            ttk.Label(rule_frame, text="Keywords:").grid(row=1, column=0, sticky="w", pady=2)
            key_text = ", ".join(rule.get('keywords', [])) or "None"
            ttk.Label(rule_frame, text=key_text, wraplength=350).grid(row=1, column=1, sticky="w")
            
            # Destination
            ttk.Label(rule_frame, text="Destination:", ).grid(row=2, column=0, sticky="w", pady=2)
            ttk.Label(rule_frame, text=rule.get('destination', 'N/A')).grid(row=2, column=1, sticky="w")

            # Edit and Delete Buttons
            button_frame = ttk.Frame(rule_frame)
            button_frame.grid(row=3, column=1, sticky="e", pady=5)

            edit_button = ttk.Button(button_frame, text="Edit", command=lambda r=rule: open_edit_window(r, config_window))
            edit_button.pack(side="left", padx=5)

            delete_button = ttk.Button(button_frame, text="Delete", command=lambda r=rule: delete_rule(r, config_window))
            delete_button.pack(side="left")

    else:
        ttk.Label(scrollable_frame, text="Could not load or find any rules in config.yaml.").pack(pady=20)

    def on_closing():
        config_window.destroy()

    config_window.protocol("WM_DELETE_WINDOW", on_closing)
    config_window.mainloop()

def open_edit_window(rule, parent_window):
    # This function would open a new window to edit the rule
    print(f"Editing rule: {rule}")


def delete_rule(rule, parent_window):
    # This function will delete the rule
    print(f"Deleting rule: {rule}")

def main():
    # Use the robust function to find the image in the resources folder
    image_path = utils.root_path("resources/broom.png")

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