# Download Organizer

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

A Windows utility that automatically organizes your Downloads folder based on configurable rules. Features a system tray interface with a configuration GUI for managing file sorting rules.

---

## Features

- **Automatic file organization**: Runs in the background and sorts files after a customizable interval of time
- **System tray integration**: Clean, unobtrusive interface with easy access
- **Configurable rules**: Create custom rules based on file extensions and keywords
- **GUI configuration**: User-friendly interface for managing sorting rules
- **Flexible destinations**: Sort files into subfolders within Downloads or absolute paths
- **Smart file handling**: Automatically handles duplicate filenames

---

## Installation

The easiest way to install Project Organizer is to download the latest installer from the official releases page.

1.  Go to the [**Releases Page**](https://github.com/Cervini/project_organizer/releases).
2.  Download the `project-organizer-setup.exe` file from the latest release.
3.  Run the installer and follow the on-screen instructions.

---

## Usage

Once installed, the application will automatically start and run silently in the background with a system tray icon.

### System Tray Interface

Right-click the system tray icon to access:
- **Configure Rules**: Open the rule management window
- **Exit**: Close the application

### Managing Rules

The configuration window allows you to:
- **Add new rules**: Create custom sorting rules
- **Edit existing rules**: Modify rule parameters
- **Delete rules**: Remove unwanted rules
- **Manual sorting**: Sort Downloads folder immediately
- **Create default folders**: Set up common file type folders

### Rule Configuration

Each rule can specify:
- **Extensions**: File types to match (e.g., `.pdf`, `.jpg`)
- **Keywords**: Filename patterns to match
- **Destination**: Where to move matching files
- **Subfolder option**: Create destination as subfolder in Downloads

---

## Building from Source

If you prefer to build the application from the source code, you will need the following tools:

* [Python 3.12+](https://www.python.org/)
* [Inno Setup](https://jrsoftware.org/isinfo.php)

Follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Cervini/organizer.git
    cd organizer
    ```

2.  **Install Python dependencies:**

    * **On Windows:**
        ```bash
        pip install -r requirements.txt
        ```
    * **On macOS and Linux:**
        First, we need to remove the Windows-specific dependency, then install the rest.
        ```bash
        sed '/pywin32-ctypes/d' requirements.txt | pip install -r /dev/stdin
        ```
        You may also need to install additional system libraries for the system tray icon to work.
        * **On Debian/Ubuntu:** `sudo apt-get install python3-gi gir1.2-gtk-3.0`
        * **On Fedora:** `sudo dnf install python3-gobject gtk3`
        * **On Arch Linux:** `sudo pacman -S python-gobject gtk3`

3.  **Bundle the app with PyInstaller:**
    ```bash
    pyinstaller --windowed --onefile main.py
    ```
    This will create an executable file inside a new `dist` folder.

4.  **(Windows Only) Create the installer with Inno Setup:**
    * Open the `installer_script.iss` file with Inno Setup.
    * From the Inno Setup menu, click `Build` > `Compile`.
    * The final `setup.exe` installer will be in the `Output` folder.

---

## Project Structure

```
organizer/
├── sources              # Application code
│   ├── main.py          # Application entry point and system tray
│   ├── gui.py           # User interface components
│   └── utils.py         # File operations and configuration management
└── resources            # Application resources (icons, etc.)
    └── config.yaml      # Rule configurations
```

---

## Default Configuration

The application comes with default rules for common file types:
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.ico`, `.svg`
- **Documents**: `.pdf`, `.docx`, `.txt`
- **Installers**: `.msi`, `.exe`
- **Archives**: `.zip`, `.rar`, `.7z`, `.gz`

---

## Future Implementations

 - [ ] Better UI design
 - [x] MacOS and Linux compatibility
 - [x] Rule priority system
 - [x] File operation logging

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.