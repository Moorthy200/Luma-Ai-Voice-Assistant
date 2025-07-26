
import datetime
import os
import sys
import time
import webbrowser
import pyautogui
import speech_recognition as sr
import random
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
from gtts import gTTS
import pygame  # Using pygame instead of playsound for audio playback
from langdetect import detect
from ollama import chat  # Ollama Llama 3 integration

# Transformers and torch for BERT sentiment analysis
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Import memory and context module functions
from memory import (
    load_user_prefs,
    add_favorite_website,
    add_frequent_app,
    update_daily_routine,
    load_mood_log,
    log_mood,
    get_last_mood,
    load_chat_history,
    update_chat_history,
    get_recent_chat_context,
)

from context import (
    add_exchange,
    get_formatted_context,
)

from auth import VoiceAuthenticator

authenticator = VoiceAuthenticator(reference_audio_path="my_voice_sample.wav", threshold=0.75)

# When you capture an audio file during wake phrase detection:
if authenticator.is_my_voice("temp_wake_audio.wav"):
    print("Voice authenticated!")
else:
    print("Voice not recognized!")

# Download required nltk packages once (if not present)
nltk.download("punkt")
nltk.download("wordnet")

# Initialize pygame mixer (do this once globally)
pygame.mixer.init()

# ----------- BERT SENTIMENT ANALYSIS -------------------

# Load pre-trained BERT sentiment model and tokenizer
# Using nlptown multilingual sentiment model that outputs 1-5 star ratings
tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

def analyze_mood_with_bert(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits.softmax(dim=1)
    rating = torch.argmax(scores) + 1  # Rating 1-5

    # Map rating to moods:
    if rating >= 4:     # 4 or 5 = Happy
        return "Happy"
    elif rating == 3:   # Neutral
        return "Neutral"
    elif rating == 2:   # Angry (somewhat negative)
        return "Angry"
    else:               # 1 = Sad
        return "Sad"

# ----------- LANGUAGE DETECTION & SPEAKING ------------------
def detect_thanglish(text):
    tamil_keywords = [
        "vanakkam", "eppadi", "iruka", "sollu", "pesu", "enna",
        "pudhu", "thunai", "mudivu", "vazhkai", "nala", "unnai",
        "kaatchi", "sirikka", "sandhosham"
    ]
    for word in tamil_keywords:
        if re.search(r"\b" + re.escape(word) + r"\b", text.lower()):
            return True
    return False

def speak(text):
    try:
        lang = detect(text)
    except:
        lang = "en"
    if detect_thanglish(text):
        lang = "ta"
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("temp_voice.mp3")

        pygame.mixer.music.load("temp_voice.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # Unload the music to release file lock (pygame 2.0+)
        try:
            pygame.mixer.music.unload()
        except AttributeError:
            # unload not supported in pygame versions < 2.0, do nothing
            pass

        # Small delay to ensure OS releases file lock
        time.sleep(0.1)

        os.remove("temp_voice.mp3")
    except Exception as e:
        print(f"Speech error: {e}")

# ----------- VOICE COMMAND LISTENING ------------------
def command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...", end="", flush=True)
        audio = r.listen(source, phrase_time_limit=10)
    try:
        print("\rRecognize...           ", end="", flush=True)
        query = r.recognize_google(audio, language="en-in")
        print(f"User said : {query}\n")
    except Exception:
        print("Say that again please")
        return None
    return query

# ----------- EMOTION-AWARE AI CHAT USING BERT & OLLAMA LLAMA3 -----------
def ai_friendly_reply(user_message):
    try:
        main_mood = analyze_mood_with_bert(user_message)

        # Log mood persistently
        log_mood(main_mood)

        prefix_map = {
            "Sad": "Oh Moorthy, you seem a little down. I'm here for you. ",
            "Happy": "That's great, Moorthy! 😊 ",
            "Angry": "Sounds frustrating! Tell me more. ",
            "Neutral": "I'm here to help, Moorthy. ",
        }
        prefix = prefix_map.get(main_mood, "")

        # Get recent chat context
        context_str = get_formatted_context()

        # Compose full prompt string for Llama 3
        full_prompt = context_str + f"\nUser: {user_message}\nNova:"

        response = chat(
            model="llama3",
            messages=[
                {"role": "system", "content": "You are a friendly, helpful AI assistant named Nova."},
                {"role": "user", "content": full_prompt},
            ],
        )
        ai_response = response["message"]["content"]

        # Update chat context history
        add_exchange(user_message, ai_response)

        return prefix + ai_response
    except Exception as e:
        return f"Sorry, I had trouble responding: {e}"

# ----------- SYSTEM AND SOCIAL APP CONTROL --------------
chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))

def social_media(command):
    browser = webbrowser.get("chrome")
    if "facebook" in command:
        speak("Opening Facebook")
        browser.open("https://www.facebook.com/")
    elif "instagram" in command:
        speak("Opening Instagram")
        browser.open("https://www.instagram.com/")
    elif "whatsapp" in command:
        speak("Opening WhatsApp")
        browser.open("https://web.whatsapp.com/")
    elif "discord" in command:
        speak("Opening Discord")
        browser.open("https://discord.com/app")
    elif "chatgpt" in command:
        speak("Opening ChatGPT")
        browser.open("https://chat.openai.com/")
    else:
        speak("No result found")

# For better maintainability, use dictionaries for app open/close commands

APP_OPEN_MAP = {
    "chrome": (f'"{chrome_path}"', "Opening Google Chrome"),
    "youtube": (r"C:\Users\Moorthy\OneDrive\Desktop\YouTube.lnk", "Opening YouTube Shortcut"),
    "calculator": ("start calc", "Opening Calculator"),
    "notepad": ("start notepad", "Opening Notepad"),
    "paint": ("start mspaint", "Opening Paint"),
    "camera": ("start microsoft.windows.camera:", "Opening Camera"),
    "explorer": ("start explorer", "Opening File Explorer"),
    "settings": ("start ms-settings:", "Opening Settings"),
    "vlc": (r'"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"', "Opening VLC Media Player"),
    "spotify": ("start spotify", "Opening Spotify"),
    "vs code": ("code", "Opening Visual Studio Code"),
    "visual studio code": ("code", "Opening Visual Studio Code"),
    "word": ("start winword", "Opening Microsoft Word"),
    "excel": ("start excel", "Opening Microsoft Excel"),
    "powerpoint": ("start powerpnt", "Opening Microsoft PowerPoint"),
    "task manager": ("start taskmgr", "Opening Task Manager"),
    "control panel": ("start control", "Opening Control Panel"),
}

def open_any_app(command):
    cmd_lower = command.lower()
    for key, (cmd, msg) in APP_OPEN_MAP.items():
        if key in cmd_lower:
            speak(msg)
            os.system(cmd)
            return
    speak("Application not recognized")

APP_CLOSE_MAP = {
    "calculator": ("taskkill /f /im CalculatorApp.exe", "Closing Calculator"),
    "notepad": ("taskkill /f /im notepad.exe", "Closing Notepad"),
    "paint": ("taskkill /f /im mspaint.exe", "Closing Paint"),
    "camera": ("taskkill /f /im WindowsCamera.exe", "Closing Camera"),
    "chrome": ("taskkill /f /im chrome.exe", "Closing Chrome"),
    "youtube": ("taskkill /f /im chrome.exe", "Closing YouTube"),
    "vlc": ("taskkill /f /im vlc.exe", "Closing VLC"),
    "spotify": ("taskkill /f /im spotify.exe", "Closing Spotify"),
    "vs code": ("taskkill /f /im Code.exe", "Closing Visual Studio Code"),
    "visual studio code": ("taskkill /f /im Code.exe", "Closing Visual Studio Code"),
    "word": ("taskkill /f /im winword.exe", "Closing Word"),
    "excel": ("taskkill /f /im excel.exe", "Closing Excel"),
    "powerpoint": ("taskkill /f /im powerpnt.exe", "Closing PowerPoint"),
    "task manager": ("taskkill /f /im taskmgr.exe", "Closing Task Manager"),
    # For explorer, restart explorer.exe instead of closing completely
    "explorer": (None, "Restarting Explorer"),
    "file explorer": (None, "Restarting Explorer"),
    "settings": ("taskkill /f /im SystemSettings.exe", "Closing Settings"),
    "control panel": ("taskkill /f /im control.exe", "Closing Control Panel"),
}

def close_any_app(command):
    cmd_lower = command.lower()
    for key, (cmd, msg) in APP_CLOSE_MAP.items():
        if key in cmd_lower:
            speak(msg)
            try:
                if key in ["explorer", "file explorer"]:
                    os.system("taskkill /f /im explorer.exe")
                    os.system("start explorer.exe")
                elif cmd is not None:
                    os.system(cmd)
            except Exception as e:
                speak(f"Failed to close {key}: {e}")
            return
    speak("App not recognized or not running.")

# -------------- SCHEDULE ----------------
def week_day():
    day = datetime.datetime.today().weekday() + 1
    return [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ][day - 1]

def schedule():
    day = week_day().lower()
    week = {
        "monday": "Team meeting at 10 AM, project work until 5 PM.",
        "tuesday": "Code review at 11 AM, client call at 4 PM.",
        "wednesday": "Development sprint, complete pending tasks.",
        "thursday": "Team presentation at 2 PM, learning session at 5 PM.",
        "friday": "Weekly report preparation and team discussion.",
        "saturday": "Personal learning, backup work, and relaxation.",
        "sunday": "Day off! Enjoy your time and recharge.",
    }
    speak(week.get(day, "No schedule available"))

# --------- WISH FUNCTION -----------
def wish():
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M %p")
    day = week_day()
    assistant_name = "Luma"

    last_mood = get_last_mood() or "neutral"

    if 5 <= hour < 12:
        msg = f"Good morning Moorthy! You felt {last_mood} yesterday. I am {assistant_name}. It's {day} and the time is {t}"
    elif 12 <= hour < 17:
        msg = f"Good afternoon Moorthy! You felt {last_mood} yesterday. I am {assistant_name}. It's {day} and the time is {t}"
    elif 17 <= hour < 21:
        msg = f"Good evening Moorthy! You felt {last_mood} yesterday. I am {assistant_name}. It's {day} and the time is {t}"
    else:
        msg = f"Good night Moorthy! You felt {last_mood} today. I am {assistant_name}. It's {day} and the time is {t}"

    print(msg)
    speak(msg)

# -------------- MAIN LOOP ----------------
if __name__ == "__main__":
    wish()
    while True:
        query = command()
        if query is None:
            continue
        query = query.lower()

        # Wake word detection
        if any(wake in query for wake in ["hey nova", "ok nova", "nova"]):
            greet = random.choice(
                [
                    "Hey Moorthy, your friend Nova here! What’s up?",
                    "Yes Moorthy, what’s on your mind?",
                    "I’m all ears, friend! How can I help?",
                ]
            )
            speak(greet)
            query = command()
            if query is None:
                continue
            query = query.lower()

        # System controls and social media commands handling
        if any(x in query for x in ["facebook", "discord", "whatsapp", "instagram", "chatgpt", "youtube"]):
            social_media(query)
        elif "university time table" in query or "schedule" in query:
            schedule()
        elif "volume up" in query:
            pyautogui.press("volumeup")
            speak("Volume increased, Moorthy!")
        elif "volume down" in query:
            pyautogui.press("volumedown")
            speak("Volume decreased.")
        elif "mute" in query:
            pyautogui.press("volumemute")
            speak("Volume muted.")
        elif "screenshot" in query:
            pyautogui.screenshot("screenshot.png")
            speak("Screenshot taken!")
        elif "scroll down" in query:
            pyautogui.scroll(-500)
            speak("Scrolling down ⬇️")
        elif "scroll up" in query:
            pyautogui.scroll(500)
            speak("Scrolling up ⬆️")
        elif "click mouse" in query:
            pyautogui.click()
            speak("Mouse clicked 🖱️")
        elif "double click" in query:
            pyautogui.doubleClick()
            speak("Double clicked!")
        elif "open" in query:
            open_any_app(query)
        elif "close" in query:
            close_any_app(query)
        elif "exit" in query or "bye" in query or "goodbye" in query:
            farewell = random.choice(
                [
                    "Goodbye Moorthy! I’ll always be here for you.",
                    "Catch you later, Moorthy. Stay awesome!",
                    "See you soon, friend!",
                ]
            )
            speak(farewell)
            sys.exit()
        else:
            # Open-ended AI chat with multi-turn context
            response = ai_friendly_reply(query)
            print(f"Luma: {response}")
            speak(response)
