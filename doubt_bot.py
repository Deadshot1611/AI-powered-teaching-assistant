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

def answer_question(transcript, question):
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
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

def handle_query(youtube_url, question):
    transcript = get_transcript(youtube_url)
    if "Error" in transcript:
        return transcript
    answer = answer_question(transcript, question)
    return answer

st.title("YouTube Video Doubt Bot")
youtube_url = st.text_input("YouTube URL", placeholder="Enter YouTube URL here...")

if youtube_url:
    transcript = get_transcript(youtube_url)
    if "Error" in transcript:
        st.write(transcript)
    else:
        st.write("Transcript successfully loaded.")
        question = st.text_input("Ask a question about the video")
        if st.button("Get Answer"):
            answer = handle_query(youtube_url, question)
            st.write("### Answer")
            st.write(answer)
