import os
import utils
import shutil

# Locate Download directory

downloads_dir = utils.locate_folder_path()

# Scan folder and check files 

# os.listdir() gives a list of every sub-directory and file name
for filename in os.listdir(downloads_dir):
    # build file path
    file_path = downloads_dir + '/' + filename
    
    # check if file
    if os.path.isfile(file_path):
        # get file name
        # get extention
        file_name, file_extension = os.path.splitext(file_path)
        # sort from name
        if "token" in file_name:
            shutil.move(file_path, r"D:\Documents\D&D\Tokens")
        # sort from exptension
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            shutil.move(file_path, downloads_dir+'/'+"img/")
        elif file_extension in ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt']:
            shutil.move(file_path, downloads_dir+'/'+"docs/")
        elif file_extension in ['.zip', '.rar', '.7z', '.gz']:
            shutil.move(file_path, downloads_dir+'/'+"archives/")
        elif file_extension in ['.exe', '.msi']:
            shutil.move(file_path, downloads_dir+'/'+"installers/")
        else:
            # extension not classified
            shutil.move(file_path, downloads_dir+'/'+"others/")