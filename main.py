import os
import json
import datetime
import random
import struct
import re
import pvporcupine
import pyaudio
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()
ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")

# 💾 Memory file path
MEMORY_FILE = "memory.json"

# 🧠 Load memory
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

# 💾 Save memory
def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# 🧠 Assistant memory
memory = load_memory()
user_name = memory.get("user_name")

# 🎯 Intents dictionary
INTENTS = {
    "greet": ["hi", "hello", "hey"],
    "set_name": ["my name is", "call me", "i am", "you can call me"],
    "get_name": ["what's my name", "do you know my name"],
    "get_time": ["what time", "tell me time", "current time"],
    "joke": ["tell me a joke", "make me laugh", "say something funny"],
    "exit": ["exit", "goodbye", "stop", "that's all"],
    "praise": ["good", "thanks", "you're great", "well done", "praising", "just saying"],
    "open_notepad": ["open notepad", "start notepad"]
}

# 📢 Speak text
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# 🎙️ Listen to microphone input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening for your command...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("⚠️ Sorry, I didn’t catch that.")
        return ""
    except sr.RequestError:
        print("⚠️ Could not connect to speech service.")
        return ""

# 🧠 Extract user's name using regex
def extract_name(command):
    command = command.lower()
    patterns = [
        r"my name is (\w+)",
        r"i am (\w+)",
        r"call me (\w+)",
        r"you can call me (\w+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(1).capitalize()
    return None

# 🔍 Detect user intent from command
def detect_intent(command):
    for intent, phrases in INTENTS.items():
        for phrase in phrases:
            if phrase in command:
                return intent
    return "unknown"

# ⚙️ Handle the identified intent
def handle_intent(intent, command):
    global user_name

    if intent == "greet":
        speak("Hello!")

    elif intent == "set_name":
        name = extract_name(command)
        if name:
            user_name = name
            memory["user_name"] = user_name
            save_memory(memory)
            speak(f"Nice to meet you, {user_name}!")
        else:
            speak("Sorry, I didn't catch your name.")

    elif intent == "get_name":
        if user_name:
            speak(f"Your name is {user_name}.")
        else:
            speak("I don't know your name yet. What should I call you?")
            response = listen()
            name = extract_name("you can call me " + response)
            if name:
                user_name = name
                memory["user_name"] = user_name
                save_memory(memory)
                speak(f"Got it. I’ll call you {user_name}.")
            else:
                speak("Still didn’t catch it.")

    elif intent == "get_time":
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}.")

    elif intent == "joke":
        speak(random.choice([
            "Why did the computer get cold? Because it left its Windows open!",
            "I'm not lazy, I'm on energy-saving mode.",
            "Why don’t scientists trust atoms? Because they make up everything!"
        ]))

    elif intent == "open_notepad":
        speak("Opening Notepad.")
        os.system("notepad.exe")

    elif intent == "exit":
        speak("Goodbye!")
        return False

    elif intent == "praise":
        speak("That means a lot. Thank you!")

    else:
        speak("Hmm, I’m not sure how to respond to that.")

    return True

# 🛑 Wake word listener using Porcupine
def wait_for_wake_word():
    print("🕵️ Barry is waiting for 'Hey Barry'...")

    porcupine = pvporcupine.create(
        keyword_paths=["wake_words/Hey-Barry_en_windows_v3_0_0.ppn"],
        access_key=ACCESS_KEY,
        sensitivities=[0.4]
    )

    audio = pyaudio.PyAudio()
    stream = audio.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            if porcupine.process(pcm):
                print("🔊 Wake word detected!")
                return
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        porcupine.delete()

# 🚀 Main loop
def main():
    while True:
        wait_for_wake_word()
        while True:
            command = listen()
            if not command:
                continue
            intent = detect_intent(command)
            should_continue = handle_intent(intent, command)
            if not should_continue:
                return

# 🔁 Run the assistant
if __name__ == "__main__":
    main()
