import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
from dotenv import load_dotenv
import os
from groq import Groq

# Load the API key from .env file
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

if not api_key:
    raise ValueError("API key is not set. Please check your .env file and ensure GROQ_API_KEY is set.")

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
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{text}"}
            ],
            max_tokens=150
        )

        if response.choices and response.choices[0].message:
            summary = response.choices[0].message.content.strip()
            return summary
        else:
            return "No summary available."
    except Exception as e:
        return f"Error in summarizing text: {str(e)}"

def handle_summary(youtube_url):
    transcript = get_transcript(youtube_url)
    if "Error" in transcript:
        return transcript
    summary = summarize_text(transcript)
    return summary

st.title("YouTube Summary Generator")
youtube_url = st.text_input("YouTube URL", placeholder="Enter YouTube URL here...")

if st.button("Generate Summary"):
    summary = handle_summary(youtube_url)
    st.text_area("Summary", summary, height=200)