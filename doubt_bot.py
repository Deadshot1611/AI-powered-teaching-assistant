import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
from dotenv import load_dotenv
import os
import openai
import tempfile
from pydub import AudioSegment
import io

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    raise ValueError("API key is not set. Please check your .env file and ensure OPENAI_API_KEY is set.")

def convert_to_supported_format(file):
    audio = AudioSegment.from_file(file)
    buffer = io.BytesIO()
    audio.export(buffer, format="mp3")
    buffer.seek(0)
    return buffer

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

def transcribe_audio(file):
    file = convert_to_supported_format(file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(file.getvalue())
        temp_file_path = temp_file.name

    try:
        with open(temp_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]
    except Exception as e:
        return f"Error in transcription: {str(e)}"
    finally:
        os.remove(temp_file_path)

def answer_question(transcript, question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Using the following transcript as context, please answer the question:\n\nTranscript:\n{transcript}\n\nQuestion:\n{question}"}
            ],
            max_tokens=150
        )
        if response.choices and response.choices[0].message:
            answer = response.choices[0].message.content.strip()
            return answer
        else:
            return "No answer available."
    except Exception as e:
        return f"Error in answering question: {str(e)}"

def handle_query(transcript, question):
    if "Error" in transcript:
        return transcript
    answer = answer_question(transcript, question)
    return answer

st.title("Video/Audio Doubt Bot")

option = st.selectbox("Choose input type", ("YouTube URL", "Upload audio/video file"))

if option == "YouTube URL":
    youtube_url = st.text_input("YouTube URL", placeholder="Enter YouTube URL here...")
    if youtube_url:
        transcript = get_transcript(youtube_url)
        if "Error" in transcript:
            st.write(transcript)
        else:
            st.write("Transcript successfully loaded.")
            question = st.text_input("Ask a question about the video")
            if st.button("Get Answer"):
                answer = handle_query(transcript, question)
                st.write("### Answer")
                st.write(answer)

elif option == "Upload audio/video file":
    uploaded_file = st.file_uploader("Choose an audio or video file", type=["mp3", "mp4", "wav"])
    if uploaded_file is not None:
        with st.spinner('Transcribing audio...'):
            transcript = transcribe_audio(uploaded_file)
        if "Error" in transcript:
            st.write(transcript)
        else:
            st.write("File successfully transcribed.")
            question = st.text_input("Ask a question about the audio/video")
            if st.button("Get Answer"):
                answer = handle_query(transcript, question)
                st.write("### Answer")
                st.write(answer)
