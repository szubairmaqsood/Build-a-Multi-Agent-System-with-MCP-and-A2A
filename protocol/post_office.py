import json
from pathlib import Path
from datetime import datetime

# Path to the JSON file where messages are stored
POST_OFFICE_PATH = Path(__file__).resolve().parent / "post_office.json"

def _ensure_file():
    """
    Ensure the post_office.json file exists.
    If it does not exist, create it with an empty list.
    """
    if not POST_OFFICE_PATH.exists():
        POST_OFFICE_PATH.write_text("[]")

def send_message(message: dict):
    """
    Send a message to the post office.
    Adds a timestamp and appends the message to the JSON file.
    """
    _ensure_file()  # Make sure the file exists
    messages = json.loads(POST_OFFICE_PATH.read_text())
    message["timestamp"] = datetime.utcnow().isoformat() + "Z"
    messages.append(message)
    POST_OFFICE_PATH.write_text(json.dumps(messages, indent=2))

def read_messages():
    """
    Read all messages from the post office.
    Returns a list of dictionaries.
    """
    _ensure_file()
    return json.loads(POST_OFFICE_PATH.read_text())

def clear_messages():
    """
    Clear all messages from the post office.
    Resets the JSON file to an empty list.
    """
    _ensure_file()
    POST_OFFICE_PATH.write_text("[]")