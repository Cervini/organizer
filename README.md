# Project Organizer

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

A simple Windows utility that runs in the background to automatically organize your files every 5 minutes.

---

## Installation

The easiest way to install Project Organizer is to download the latest installer from the official releases page.

1.  Go to the [**Releases Page**](https://github.com/Cervini/project_organizer/releases).
2.  Download the `project-organizer-setup.exe` file from the latest release.
3.  Run the installer and follow the on-screen instructions.

---

## Usage

Once installed, the application will automatically start and run silently in the background. It will perform its sorting task every 5 minutes. There is no user interface; the program manages itself.

To stop the application, you will need to uninstall it from the Windows "Apps & features" settings.

---

## Building from Source

If you prefer to build the application from the source code, you will need the following tools:

* [Python 3.12+](https://www.python.org/)
* [Inno Setup](https://jrsoftware.org/isinfo.php)

Follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Cervini/project_organizer.git](https://github.com/Cervini/project_organizer.git)
    cd project_organizer
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Bundle the app with PyInstaller:**
    ```bash
    pyinstaller --windowed --onefile main.py
    ```
    This will create a `main.exe` file inside a new `dist` folder.

4.  **Create the installer with Inno Setup:**
    * Open the `installer_script.iss` file with Inno Setup.
    * From the Inno Setup menu, click `Build` > `Compile`.
    * The final `setup.exe` installer will be in the `Output` folder.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.