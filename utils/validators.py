import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_resume_file(file_storage):
    if file_storage is None:
        raise ValueError("Resume file is required.")

    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ValueError("Please select a valid resume file.")

    extension = os.path.splitext(filename)[1].lower().lstrip('.')
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF and DOCX files are allowed.")

    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError("Resume file size must be under 5MB.")

    return filename
