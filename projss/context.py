# context.py
import json
import os
from typing import List, Dict

CONTEXT_FOLDER = "memory"
os.makedirs(CONTEXT_FOLDER, exist_ok=True)
CONTEXT_FILE = os.path.join(CONTEXT_FOLDER, "chat_history.json")
MAX_CONTEXT_TURNS = 10  # Number of dialogue pairs to keep

def load_context() -> List[Dict[str, str]]:
    """Load recent user-Nova exchanges from file."""
    try:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"[context.py] Error loading context: {e}")
        return []

def save_context(history: List[Dict[str, str]]) -> None:
    """Save user-Nova exchanges to context file."""
    try:
        with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"[context.py] Error saving context: {e}")

def add_exchange(user_message: str, nova_reply: str) -> None:
    """Add a new Q&A turn and enforce context window size."""
    history = load_context()
    history.append({"user": user_message, "nova": nova_reply})
    if len(history) > MAX_CONTEXT_TURNS:
        history = history[-MAX_CONTEXT_TURNS:]
    save_context(history)

def get_formatted_context() -> str:
    """Format rolling chat history for conversation-aware LLM prompts."""
    history = load_context()
    formatted = ""
    for turn in history:
        formatted += f"User: {turn['user']}\nNova: {turn['nova']}\n"
    return formatted

def clear_context() -> None:
    """Optional: Clear chat context (for privacy or resetting)."""
    save_context([])

# Optional: Suggest follow-up if a previous topic is detected in context
def suggest_followup(topic_keywords=None) -> str:
    if topic_keywords is None:
        topic_keywords = ["project", "meeting", "reminder"]
    context = load_context()
    if context:
        last_user = context[-1]["user"].lower()
        for word in topic_keywords:
            if word in last_user:
                return f"Would you like to continue our last discussion about {word}?"
    return ""

# Optional direct module testing
if __name__ == "__main__":
    print("Testing context module:")
    add_exchange("How's the weather?", "It's sunny today!")
    add_exchange("Tell me a joke.", "Why did the chicken cross the road? To get to the other side!")
    print(get_formatted_context())
