import os
import utils
from pathlib import Path

# Locate Download directory

downloads_dir = utils.locate_folder_path()

# Scan folder and check files 

# os.listdir() gives a list of every sub-directory and file name
for filename in os.listdir(downloads_dir):
    
    file_path = downloads_dir + '/' + filename # see this
    
    # check if file
    if os.path.isfile(file_path):
        # get file name
        # get extention
        file_name, file_extension = os.path.splitext(file_path)

        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            print(f"  -> '{utils.filter_file_name(file_name)}' img")
            
        elif file_extension in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt']:
            print(f"  -> '{utils.filter_file_name(file_name)}' doc")
            
        elif file_extension in ['.zip', '.rar', '.7z', '.gz']:
            print(f"  -> '{utils.filter_file_name(file_name)}' archive")

        elif file_extension in ['.exe', '.msi']:
            print(f"  -> '{utils.filter_file_name(file_name)}' installer")
            
        else:
            # Se non riconosciamo l'estensione, lo segnaliamo
            print(f"  -> '{utils.filter_file_name(file_name)}' -> other")

print("\n'Dry run' ended.")