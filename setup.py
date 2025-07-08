import sys
from cx_Freeze import setup, Executable

# This ensures the black console window doesn't appear when your app runs
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="DownloadOrganizer",
    version="1.2.0",
    description="A service to automatically organize Download folder.",
    
    # Tells cx_Freeze that your main script is "main.py"
    executables=[Executable("main.py", base=base)],
    
    # Specifies any packages your script needs to run
    options={
        "build_exe": {
            "packages": ["schedule", "os", "time"],
        }
    },
)