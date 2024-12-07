import os


UPLOAD_FOLDER = "uploads"


def save_file(file, extension: str, task_id: str):
    task_folder = get_task_folder(task_id)
    filepath = os.path.join(task_folder, f"{task_id}.{extension}")
    file.save(filepath)
    return filepath


def get_task_folder(task_id: str):
    folder_path = os.path.join(UPLOAD_FOLDER, task_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path
