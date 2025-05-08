import streamlit as st
import pyttsx3
import speech_recognition as sr
from difflib import SequenceMatcher
import string
import time
import tempfile

# Set page config
st.set_page_config(page_title="BPO Pronunciation Practice", layout="centered")

# Initialize TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

def speak_text_to_file(text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts_engine.save_to_file(text, fp.name)
        tts_engine.runAndWait()
        return fp.name

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now.")
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

    try:
        result = recognizer.recognize_google(audio)
        return result
    except sr.UnknownValueError:
        return "[Could not understand]"
    except sr.RequestError:
        return "[STT API error]"

def clean_text(text):
    return text.translate(str.maketrans('', '', string.punctuation)).lower()

def highlight_differences(expected, actual):
    expected_words = clean_text(expected).split()
    actual_words = clean_text(actual).split()
    matcher = SequenceMatcher(None, expected_words, actual_words)
    feedback = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == 'equal':
            for word in expected_words[i1:i2]:
                feedback.append(f"✅ **{word}**")
        elif opcode == 'replace':
            feedback.append(f"❌ **Expected**: {' '.join(expected_words[i1:i2])} | **Heard**: {' '.join(actual_words[j1:j2])}")
        elif opcode == 'delete':
            feedback.append(f"❌ **Missed**: {' '.join(expected_words[i1:i2])}")
        elif opcode == 'insert':
            feedback.append(f"❌ **Extra**: {' '.join(actual_words[j1:j2])}")
    return feedback

# UI
st.title("🗣️ BPO English Practice Tool")
sentence = st.text_input("Sentence to practice:", value="Please hold, while I transfer your call.")

if st.button("🔊 Play Sentence"):
    path = speak_text_to_file(sentence)
    audio_file = open(path, 'rb')
    st.audio(audio_file.read(), format='audio/mp3')

if st.button("🎤 Start Recording"):
    with st.spinner("Listening..."):
        recognized = recognize_speech_from_mic()
        st.success(f"You said: {recognized}")
        feedback = highlight_differences(sentence, recognized)
        for item in feedback:
            st.markdown(item)
