import os
import io
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import logging
import warnings
from pydub import AudioSegment
import tempfile
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

def convert_to_supported_format(file):
    audio = AudioSegment.from_file(file)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)
    return buffer

def transcribe_audio(file):
    logging.info("Transcribing audio file")
    file = convert_to_supported_format(file)
    logging.info("Converted file to WAV format")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(file.getvalue())
        temp_file_path = temp_file.name

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with open(temp_file_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]
    except Exception as e:
        logging.error(f"Error in transcription: {str(e)}")
        return f"Error in transcription: {str(e)}"
    finally:
        os.remove(temp_file_path)

def get_transcript(url):
    try:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if match:
            video_id = match.group(1)
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([entry['text'] for entry in transcript])
            return transcript_text
        else:
            return "No video ID found in URL."
    except Exception as e:
        return f"Error: {str(e)}"

def summarize_text(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{text}"}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error in summarizing text: {str(e)}"

def handle_summary(transcript_text):
    if "Error" in transcript_text:
        return transcript_text
    summary = summarize_text(transcript_text)
    return summary

st.title("YouTube Summary Generator")

option = st.selectbox("Choose input type", ("YouTube URL", "Upload audio/video file"))

if option == "YouTube URL":
    youtube_url = st.text_input("YouTube URL", placeholder="Enter YouTube URL here...")
    if st.button("Generate Summary"):
        transcript = get_transcript(youtube_url)
        summary = handle_summary(transcript)
        st.text_area("Summary", summary, height=200)

elif option == "Upload audio/video file":
    uploaded_file = st.file_uploader("Choose an audio or video file", type=["mp3", "wav", "mp4", "mov"])
    if uploaded_file is not None:
        if st.button("Generate Summary"):
            with st.spinner('Transcribing audio...'):
                transcript_text = transcribe_audio(uploaded_file)
            summary = handle_summary(transcript_text)
            st.text_area("Summary", summary, height=200)

