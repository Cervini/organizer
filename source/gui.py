import tkinter as tk
from tkinter import ttk
import threading
import utils


def open_config_window_threaded():
    """Opens the main configuration window in a separate thread."""
    config_thread = threading.Thread(target=open_config_window)
    config_thread.daemon = True
    config_thread.start()


def open_delete_window_threaded(rule, parent_window, frame_to_refresh):
    """Starts the delete confirmation window in a new thread."""
    delete_thread = threading.Thread(
        target=open_delete_window,
        args=(rule, parent_window, frame_to_refresh)
    )
    delete_thread.daemon = True
    delete_thread.start()


def open_edit_window_threaded(rule, parent_window, frame_to_refresh):
    """Starts the rule editing window in a new thread."""
    edit_thread = threading.Thread(
        target=open_edit_window,
        args=(rule, parent_window, frame_to_refresh)
    )
    edit_thread.daemon = True
    edit_thread.start()


def open_add_window_threaded(parent_window, frame_to_refresh):
    """Starts the rule adding window in a new thread."""
    add_thread = threading.Thread(
        target=open_add_window,
        args=(parent_window, frame_to_refresh)
    )
    add_thread.daemon = True
    add_thread.start()


def refresh_rules_list(frame):
    """Clears and redraws all rule cards in the given frame."""
    # Destroy all current widgets in the frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Reload the rules and rebuild the UI
    rules = utils.load_config()
    if rules:
        create_rule_cards(frame, rules) # Use the refactored card creation logic
    else:
        ttk.Label(frame, text="Could not load or find any rules in config.yaml.").pack(pady=20)


def create_rule_cards(parent_frame, rules):
    """Creates and packs all the rule card widgets into the parent_frame."""
    # Get the parent window from the frame
    config_window = parent_frame.winfo_toplevel()
    for rule in rules:
        rule_frame = ttk.LabelFrame(parent_frame, text=f"{rule.get('name', 'N/A')}", padding="10")
        rule_frame.pack(pady=10, padx=10, fill="x", expand=True)

        ttk.Label(rule_frame, text="Extensions:").grid(row=0, column=0, sticky="w", pady=2)
        ext_text = ", ".join(rule.get('extensions', [])) or "Any"
        ttk.Label(rule_frame, text=ext_text, wraplength=350).grid(row=0, column=1, sticky="w")

        ttk.Label(rule_frame, text="Keywords:").grid(row=1, column=0, sticky="w", pady=2)
        key_text = ", ".join(rule.get('keywords', [])) or "None"
        ttk.Label(rule_frame, text=key_text, wraplength=350).grid(row=1, column=1, sticky="w")

        ttk.Label(rule_frame, text="Destination:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(rule_frame, text=rule.get('destination', 'N/A')).grid(row=2, column=1, sticky="w")

        button_frame = ttk.Frame(rule_frame)
        button_frame.grid(row=3, column=1, sticky="e", pady=5)

        edit_button = ttk.Button(
            button_frame,
            text="Edit",
            command=lambda r=rule: open_edit_window_threaded(r, config_window, parent_frame)
        )
        edit_button.pack(side="left")

        delete_button = ttk.Button(
            button_frame,
            text="Delete",
            command=lambda r=rule: open_delete_window_threaded(r, config_window, parent_frame)
        )
        delete_button.pack(side="left")


def open_config_window():
    """Opens a window to see the rules applied"""
    config_window = tk.Tk()
    config_window.title("Configure Rules")
    w, h = 600, 500
    ws, hs = config_window.winfo_screenwidth(), config_window.winfo_screenheight()
    x, y = (ws/2) - (w/2), (hs/2) - (h/2)
    config_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    main_frame = tk.Frame(config_window)
    main_frame.pack(fill='both', expand=True)

    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill='x', padx=10, pady=5)

    add_button = ttk.Button(
        top_frame,
        text="Add New Rule",
        # The command will call a new threaded function
        command=lambda: open_add_window_threaded(config_window, scrollable_frame)
    )
    add_button.pack(side="left")
    sort_button = ttk.Button(
        top_frame,
        text="Sort Downloads folder",
        # The command will sort Download folder
        command=lambda: utils.file_sorter()
    )
    sort_button.pack(side="left")
    create_default_folders_button = ttk.Button(
        top_frame,
        text="Create deafult folders",
        command=lambda: utils.create_folders()
    )
    create_default_folders_button.pack(side="left")

    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")

    rules = utils.load_config()
    if rules:
        # Initial creation of rule cards
        create_rule_cards(scrollable_frame, rules)
    else:
        ttk.Label(scrollable_frame, text="Could not load or find any rules in config.yaml.").pack(pady=20)

    config_window.mainloop()


def open_delete_window(rule, parent_window, frame_to_refresh):
    """Opens a window to delete a rule"""
    delete_window = tk.Toplevel(parent_window)
    delete_window.title("Confirm Delete")
    w, h = 250, 100
    ws, hs = delete_window.winfo_screenwidth(), delete_window.winfo_screenheight()
    x, y = (ws/2) - (w/2), (hs/2) - (h/2)
    delete_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    delete_window.grab_set()
    delete_window.transient(parent_window)

    label = ttk.Label(delete_window, text="Are you sure you want to delete this rule?")
    label.pack(pady=10)

    button_frame = ttk.Frame(delete_window)
    button_frame.pack(pady=5)

    def confirm_delete():
        """Deletes the rule, closes the pop-up, and refreshes the list."""
        utils.delete_rule_from_config(rule.get("name"))
        delete_window.destroy()
        # This is the key change: just refresh the list in the existing window.
        refresh_rules_list(frame_to_refresh)

    yes_button = ttk.Button(button_frame, text="YES", command=confirm_delete)
    yes_button.pack(side="left", padx=10)

    no_button = ttk.Button(button_frame, text="NO", command=delete_window.destroy)
    no_button.pack(side="left", padx=10)


def open_edit_window(rule, parent_window, frame_to_refresh):
    """Opens a window to edit a rule"""
    edit_window = tk.Toplevel(parent_window)
    edit_window.title("Edit "+ rule.get("name"))
    w, h = 400, 250
    ws, hs = edit_window.winfo_screenwidth(), edit_window.winfo_screenheight()
    x, y = (ws/2) - (w/2), (hs/2) - (h/2)
    edit_window.geometry('%dx%d+%d+%d' % (w,h,x,y))

    edit_window.grab_set()
    edit_window.transient(parent_window)

    # --- Create a frame for the form ---
    form_frame = ttk.Frame(edit_window, padding="10")
    form_frame.pack(fill="both", expand=True)

    # --- Tkinter variables to hold form data ---
    name_var = tk.StringVar(value=rule.get("name", ""))
    extensions_var = tk.StringVar(value=", ".join(rule.get("extensions", [])))
    keywords_var = tk.StringVar(value=", ".join(rule.get("keywords", [])))
    destination_var = tk.StringVar(value=rule.get("destination", ""))
    sub_var = tk.BooleanVar(value=rule.get("sub", False))

    # --- Form Fields ---
    # Rule Name (read-only, as it's the identifier)
    ttk.Label(form_frame, text="Rule Name:").grid(row=0, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=name_var, state="readonly").grid(row=0, column=1, sticky="ew", pady=2)

    # Extensions
    ttk.Label(form_frame, text="Extensions:").grid(row=1, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=extensions_var).grid(row=1, column=1, sticky="ew", pady=2)

    # Keywords
    ttk.Label(form_frame, text="Keywords:").grid(row=2, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=keywords_var).grid(row=2, column=1, sticky="ew", pady=2)

    # Destination
    ttk.Label(form_frame, text="Destination:").grid(row=3, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=destination_var).grid(row=3, column=1, sticky="ew", pady=2)

    # Sub-folder Checkbox
    ttk.Checkbutton(form_frame, text="Create as sub-folder in Downloads", variable=sub_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)

    # Make the second column stretchable
    form_frame.columnconfigure(1, weight=1)

    # --- Save and Cancel Buttons ---
    button_frame = ttk.Frame(edit_window, padding=(0, 0, 10, 10))
    button_frame.pack(fill="x")

    def save_changes():
        """Gathers data, updates the config, and refreshes the main window."""
        # Prepare data from form
        # Split comma-separated strings into lists, stripping whitespace
        extensions_list = [ext.strip() for ext in extensions_var.get().split(',') if ext.strip()]
        keywords_list = [key.strip() for key in keywords_var.get().split(',') if key.strip()]

        # Create the updated rule dictionary
        updated_rule = {
            "name": name_var.get(),
            "extensions": extensions_list,
            "keywords": keywords_list,
            "destination": destination_var.get(),
            "sub": sub_var.get()
        }

        # Save to config file and refresh UI
        utils.update_rule(updated_rule)
        edit_window.destroy()
        refresh_rules_list(frame_to_refresh)

    ttk.Button(button_frame, text="Save", command=save_changes).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side="right")


def open_add_window(parent_window, frame_to_refresh):
    """Opens a window to create a new rule."""
    add_window = tk.Toplevel(parent_window)
    add_window.title("Add New Rule")
    w, h = 350, 200
    ws, hs = add_window.winfo_screenwidth(), add_window.winfo_screenheight()
    x, y = (ws/2) - (w/2), (hs/2) - (h/2)
    add_window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    add_window.grab_set()
    add_window.transient(parent_window)

    form_frame = ttk.Frame(add_window, padding="10")
    form_frame.pack(fill="both", expand=True)

    # Variables for the new rule's data
    name_var = tk.StringVar()
    extensions_var = tk.StringVar()
    keywords_var = tk.StringVar()
    destination_var = tk.StringVar()
    sub_var = tk.BooleanVar(value=True) # Default to true

    # --- Form Fields (Name is now editable) ---
    ttk.Label(form_frame, text="Rule Name:").grid(row=0, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=name_var).grid(row=0, column=1, sticky="ew", pady=2)

    ttk.Label(form_frame, text="Extensions:").grid(row=1, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=extensions_var).grid(row=1, column=1, sticky="ew", pady=2)

    ttk.Label(form_frame, text="Keywords:").grid(row=2, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=keywords_var).grid(row=2, column=1, sticky="ew", pady=2)

    ttk.Label(form_frame, text="Destination:").grid(row=3, column=0, sticky="w", pady=2)
    ttk.Entry(form_frame, textvariable=destination_var).grid(row=3, column=1, sticky="ew", pady=2)

    ttk.Checkbutton(form_frame, text="Create as sub-folder in Downloads", variable=sub_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
    form_frame.columnconfigure(1, weight=1)

    # --- Save and Cancel Buttons ---
    button_frame = ttk.Frame(add_window, padding=(0, 0, 10, 10))
    button_frame.pack(fill="x")

    def save_new_rule():
        """Gathers data, creates a new rule, and saves it."""
        rule_name = name_var.get().strip()
        if not rule_name:
            # Simple validation: prevent saving with no name
            print("Error: Rule name cannot be empty.")
            return

        extensions_list = [ext.strip() for ext in extensions_var.get().split(',') if ext.strip()]
        keywords_list = [key.strip() for key in keywords_var.get().split(',') if key.strip()]

        new_rule = {
            "name": rule_name,
            "extensions": extensions_list,
            "keywords": keywords_list,
            "destination": destination_var.get().strip(),
            "sub": sub_var.get()
        }

        utils.add_rule(new_rule) # Call the new utility function
        add_window.destroy()
        refresh_rules_list(frame_to_refresh)

    ttk.Button(button_frame, text="Save", command=save_new_rule).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side="right")