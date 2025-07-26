Luma: Emotion-Aware AI Voice Assistant
Luma is an advanced AI-powered voice assistant that can understand emotions, maintain multi-turn conversational context, and control applications & social media. It supports English, Tamil, and Thanglish with automatic language detection and offers voice authentication for security.

✨ Key Features
🎙️ Voice Authentication: Authenticate users using a reference voice sample.

🧠 Context-Aware Conversations: Multi-turn memory using Ollama LLaMA 3.

😊 Emotion Detection: Uses BERT-based sentiment analysis to detect moods (Happy, Sad, Angry, Neutral) and respond empathetically.

🌍 Multilingual Support: English, Tamil & Thanglish detection with speech output.

🖥️ System & App Control: Open, close, and manage popular applications with commands.

🌐 Social Media Automation: Quick access to Facebook, Instagram, WhatsApp, Discord, ChatGPT, and YouTube.

🔊 Natural Speech Output: Uses gTTS with pygame for human-like voice responses.

📅 Daily Schedule Announcements: Personalized greetings with your last mood and day schedule.

🛠️ Tech Stack
Programming Language: Python 3.9+

Libraries:

Speech Recognition: speech_recognition, langdetect

NLP & AI: transformers, torch, nltk, ollama

TTS & Audio: gTTS, pygame

System Control: os, pyautogui, webbrowser

AI Models:

Sentiment Analysis: nlptown/bert-base-multilingual-uncased-sentiment

Conversational AI: Ollama LLaMA 3

📂 Project Structure
bash
Copy
Edit
Luma/
├── assistant.py          # Main application
├── memory.py             # Stores chat history, user preferences, and mood logs
├── context.py            # Context management for multi-turn conversation
├── auth.py               # Voice authentication module
├── requirements.txt      # Required Python libraries
└── README.md             # Project documentation
⚡ Installation & Setup
Clone the repository:

bash
Copy
Edit
git clone https://github.com/your-username/luma.git
cd luma
Create and activate a virtual environment:

bash
Copy
Edit
python -m venv environment
source environment/bin/activate   # For Linux/Mac
environment\Scripts\activate      # For Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Download required NLTK models:

python
Copy
Edit
import nltk
nltk.download("punkt")
nltk.download("wordnet")
Set up Ollama LLaMA 3 (for AI chat):
Install Ollama and pull the LLaMA 3 model:

bash
Copy
Edit
ollama pull llama3
Voice Authentication:

Record your reference voice sample as my_voice_sample.wav.

Luma will verify your voice before activation.

▶️ Running Luma
bash
Copy
Edit
python assistant.py
Use wake words: "Hey Luma", "Ok Luma", or "Luma".

Give commands like:

"Open Chrome"

"Close Spotify"

"What's my schedule?"

"How are you today?" (for chat)

🖼️ Demo Screenshot / GIF (Optional)
Add screenshots or GIF showing Luma in action.

🚀 Future Enhancements
Replace gTTS with Edge-TTS or OpenAI TTS for more natural voice.

Add smart reminders and alarms.

Add API integration for weather, news, and calendar events.

GUI-based interface for better usability.

📜 License
This project is licensed under the Apache License.

👨‍💻 Author
Moorthy M – B.Tech AI & Data Science


