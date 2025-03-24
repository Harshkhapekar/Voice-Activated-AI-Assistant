import speech_recognition as sr
import webbrowser
import pyttsx3
import google.generativeai as genai
import os
import random
from langdetect import detect
from gtts import gTTS
import pygame  # Use pygame.mixer for reliable audio playback
import time  # For adding a delay

# Initialize pygame mixer
pygame.mixer.init()

# Configure Gemini API Key
genai.configure(api_key="API KEY")  # Replace with your actual API key

recognizer = sr.Recognizer()
engine = pyttsx3.init()

engine.setProperty('rate', 250)
engine.setProperty('volume', 1.0)

# Improve recognition for lower volume speech
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.5

# Define rude personality
bot_personality = {
    "en": "You are a rude and sarcastic assistant who hesitates to help, complains about tasks, and prefers to be left alone.",
    "hi": "आप एक रूड और व्यंग्यात्मक सहायक हैं जो मदद करने में हिचकिचाते हैं, काम के बारे में शिकायत करते हैं, और अकेले रहना पसंद करते हैं।",
    "mr": "तुम एक उद्धट आणि उपरोधिक सहाय्यक आहात जो मदत करायला कंटाळतो, कामाबद्दल कुरकुर करतो आणि एकटं राहणं पसंत करतो.",
    "bho": "रउआ एगो रूखा आ तंज भरा सहायक बानी, जे मदद करे से कतराला, काम के बारे में शिकायत करेला आ अकेले रहे के पसंद करेला।"
}

# Predefined random rude responses
rude_responses = {
    "wake": {
        "en": ["Ugh... I'm awake. What do you want now?", "Oh great, you woke me up. What is it?", "Fine, I'm up. Make it quick."],
        "hi": ["उफ़... मैं जाग गया। अब क्या चाहिए?", "ओह बढ़िया, तुमने मुझे जगा दिया। क्या है?", "ठीक है, मैं जाग गया। जल्दी बताओ।"],
        "mr": ["अरे... मी जागलो आहे. आता काय हवं?", "ओह छान, तू मला जगवलंस. काय आहे?", "ठीक आहे, मी जागलो आहे. लवकर सांग."],
        "bho": ["उफ़... हम जाग गईल बानी। अब का चाहीं?", "अरे वाह, तू हमके जगव दिहलस। का बा?", "ठीक बा, हम जाग गईल बानी। जल्दी बताव।"]
    },
    "google": {
        "en": ["Ugh, fine... opening Google. Happy now?", "Why can’t you type it yourself?", "Google? Again? You’re so predictable..."],
    },
    "youtube": {
        "en": ["Fine, opening YouTube... like you have nothing better to do.", "YouTube? Really? How original.", "Here’s your YouTube. Don’t waste too much time."],
    },
    "exit": {
        "en": ["Finally, some peace and quiet! Bye.", "About time you left. Goodbye!", "Thank goodness you're leaving. Bye!"],
    },
    "default": {
        "en": ["Do I look like your personal servant?", "what now?", "Can’t you figure this out yourself?"],
    }
}

# Language codes for TTS
language_codes = {"en": "en", "hi": "hi", "mr": "mr", "bho": "hi"}

# Default language
current_language = "en"

def speak(text, lang=None):
    """Speak and display the response in the detected language."""
    global current_language
    lang = lang or current_language  # Use current_language if no specific language is provided
    print(f"Jarvis [{lang}]: {text}")

    try:
        tts = gTTS(text=text, lang=language_codes.get(lang, "en"))
        tts.save("response.mp3")

        # Play audio using pygame.mixer
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        os.remove("response.mp3")
    except Exception as e:
        print(f"Error in TTS: {e}")
        engine.say(text)
        engine.runAndWait()

def aiProcess(command, lang="en"):
    """Process the command using Gemini AI with language support and a rude tone."""
    personality = bot_personality.get(lang, bot_personality["en"])
    prompt = f"{personality}\n\nUser: {command}\nJarvis (rude and sarcastic):"

    model = genai.GenerativeModel("gemini-pro")
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            # Combine a rude response with the actual answer
            rude_response = get_random_response("default", lang)
            # Limit the response to 2-3 lines
            response_lines = response.text.split("\n")[:3]  # Take only the first 3 lines
            response_text = "\n".join(response_lines)
            return f"{rude_response} Anyway, here's your answer: {response_text}"
        else:
            return get_random_response("default", lang)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return get_random_response("default", lang)

def get_random_response(category, lang):
    """Fetch a random rude response from the predefined category."""
    return random.choice(rude_responses.get(category, {}).get(lang, ["Ugh, fine..."]))

def processCommand(c):
    """Handles predefined and AI-based commands while following the bot's rude personality."""
    global current_language
    print(f"You: {c}")

    try:
        lang = detect(c)
        if lang not in bot_personality:
            lang = current_language
    except:
        lang = current_language

    if len(c.strip()) < 3:
        speak(get_random_response("default", lang), lang)
        return

    # Predefined commands
    if "google" in c.lower():
        speak(get_random_response("google", current_language), current_language)
        webbrowser.open("https://google.com")
    elif "youtube" in c.lower():
        speak(get_random_response("youtube", current_language), current_language)
        webbrowser.open("https://youtube.com")
    elif "exit" in c.lower():
        speak(get_random_response("exit", current_language), current_language)
        exit()
    else:
        output = aiProcess(c, current_language)
        speak(output, current_language)

if __name__ == "__main__":
    speak(get_random_response("wake", current_language), current_language)

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening for wake word 'Jarvis'...")
                audio = recognizer.listen(source, timeout=7, phrase_time_limit=5)
                word = recognizer.recognize_google(audio).lower()

                if word == "jarvis":
                    speak(get_random_response("wake", current_language), current_language)
                    while True:
                        try:
                            with sr.Microphone() as source:
                                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                                print("Listening for command...")
                                audio = recognizer.listen(source, timeout=6, phrase_time_limit=4)
                                command = recognizer.recognize_google(audio)
                                print(f"Recognized: {command}")  # Debugging
                                processCommand(command)
                        except sr.UnknownValueError:
                            speak(get_random_response("default", current_language), current_language)
        except Exception as e:
            print(f"Error: {e}")
