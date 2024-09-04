import os


def clean_uploads_folder(folder_path, max_files=20, files_to_delete=10):
    # Get a list of all files in the folder
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # Sort files by last modification time
    files.sort(key=os.path.getmtime)

    if len(files) > max_files:
        for file in files[:files_to_delete]:
            os.remove(file)