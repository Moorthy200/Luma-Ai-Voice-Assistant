import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Base folder for memory JSON files
MEMORY_DIR = "memory"

# Ensure memory directory exists
os.makedirs(MEMORY_DIR, exist_ok=True)

# File paths
USER_PREFS_FILE = os.path.join(MEMORY_DIR, "user_prefs.json")
MOOD_LOG_FILE = os.path.join(MEMORY_DIR, "mood_log.json")
CHAT_HISTORY_FILE = os.path.join(MEMORY_DIR, "chat_history.json")


def save_to_file(data: Union[Dict, List], filename: str) -> None:
    """
    Save data (dictionary or list) to a JSON file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"[memory.py] Error saving to {filename}: {e}")


def load_from_file(filename: str) -> Optional[Union[Dict, List]]:
    """
    Load and return data from a JSON file.
    Returns None if the file does not exist or cannot be read.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        # File doesn't exist yet
        return None
    except Exception as e:
        print(f"[memory.py] Error loading {filename}: {e}")
        return None


# === User Preferences Functions ===

def load_user_prefs() -> Dict[str, Any]:
    """
    Load user preferences from JSON file.
    Returns an empty dict with default keys if none found.
    """
    prefs = load_from_file(USER_PREFS_FILE)
    if prefs is None:
        prefs = {
            "favorite_websites": [],
            "daily_routines": {},
            "frequently_used_apps": []
        }
    return prefs


def save_user_prefs(prefs: Dict[str, Any]) -> None:
    """
    Save user preferences dictionary to JSON file.
    """
    save_to_file(prefs, USER_PREFS_FILE)


def add_favorite_website(url: str) -> None:
    """
    Add a new favorite website to user preferences if not already present.
    """
    prefs = load_user_prefs()
    if url not in prefs["favorite_websites"]:
        prefs["favorite_websites"].append(url)
        save_user_prefs(prefs)


def add_frequent_app(app_name: str) -> None:
    """
    Add a frequently used app to preferences if not already present.
    Case-insensitive check.
    """
    prefs = load_user_prefs()
    apps_lower = [app.lower() for app in prefs["frequently_used_apps"]]
    if app_name.lower() not in apps_lower:
        prefs["frequently_used_apps"].append(app_name)
        save_user_prefs(prefs)


def update_daily_routine(time_of_day: str, activity: str) -> None:
    """
    Update a daily routine activity for morning/afternoon/evening.
    """
    prefs = load_user_prefs()
    prefs["daily_routines"][time_of_day.lower()] = activity
    save_user_prefs(prefs)


# === Mood History Functions ===

def load_mood_log() -> List[Dict[str, str]]:
    """
    Load mood log list from JSON file.
    Returns empty list if none found.
    """
    moods = load_from_file(MOOD_LOG_FILE)
    return moods if moods is not None else []


def log_mood(mood: str) -> None:
    """
    Append a mood entry with current timestamp to the mood log.
    """
    moods = load_mood_log()
    mood_entry = {"timestamp": datetime.now().isoformat(), "mood": mood}
    moods.append(mood_entry)
    save_to_file(moods, MOOD_LOG_FILE)


def get_last_mood() -> Optional[str]:
    """
    Return the last recorded mood, or None if no moods logged.
    """
    moods = load_mood_log()
    if moods:
        return moods[-1]["mood"]
    return None


# === Chat History Functions ===

MAX_CHAT_ENTRIES = 10


def load_chat_history() -> List[Dict[str, str]]:
    """
    Load the chat history list from file.
    Returns empty list if no history found.
    """
    history = load_from_file(CHAT_HISTORY_FILE)
    return history if history is not None else []


def update_chat_history(user_message: str, nova_reply: str) -> None:
    """
    Append a new user-Nova chat exchange to history,
    keeping only the last MAX_CHAT_ENTRIES entries.
    """
    history = load_chat_history()
    history.append({"user": user_message, "nova": nova_reply})
    # Trim history if exceeding max entries
    if len(history) > MAX_CHAT_ENTRIES:
        history = history[-MAX_CHAT_ENTRIES:]
    save_to_file(history, CHAT_HISTORY_FILE)


def get_recent_chat_context() -> List[Dict[str, str]]:
    """
    Return the recent chat exchanges for context (last 10 by default).
    """
    history = load_chat_history()
    return history[-MAX_CHAT_ENTRIES:]


# === Optional Clear/Reset Functions ===

def clear_user_prefs() -> None:
    save_user_prefs({
        "favorite_websites": [],
        "daily_routines": {},
        "frequently_used_apps": []
    })


def clear_mood_log() -> None:
    save_to_file([], MOOD_LOG_FILE)


def clear_chat_history() -> None:
    save_to_file([], CHAT_HISTORY_FILE)


# Test code (run only if executed directly)
if __name__ == "__main__":
    print("Testing memory.py functions...")

    print("Loading user prefs:")
    prefs = load_user_prefs()
    print(prefs)

    print("Adding favorite website 'https://example.com'")
    add_favorite_website("https://example.com")
    print(load_user_prefs())

    print("Logging mood: Happy")
    log_mood("Happy")
    print(load_mood_log())

    print("Adding chat entry")
    update_chat_history("Hello Nova, how are you?", "I'm good, Moorthy! How can I help?")
    print(load_chat_history())
