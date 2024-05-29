import openai
import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi
import re
from dotenv import load_dotenv
import os

# Load the API key from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

print("API Key:", os.getenv('OPENAI_API_KEY'))

if not api_key:
    raise ValueError("API key is not set. Please check your .env file and ensure OPENAI_API_KEY is set.")

# Ensure the API key is correctly formatted
if not api_key.startswith("sk-") or len(api_key) < 20:
    raise ValueError("Malformed API key. Please check your .env file.")

openai.api_key = api_key

def get_transcript(url):
    try:
        video_id = re.search(r"v=([^&]+)", url)
        if video_id:
            video_id = video_id.group(1)
        else:
            video_id = url.split('/')[-1].split('?')[0]  # Fallback to extract from short URL

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        output = ''
        for x in transcript:
            sentence = x['text']
            output += f' {sentence}\n'
        return output, None
    except Exception as e:
        return None, f"Error in fetching transcript: {str(e)}"

def summarize_text(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Please summarize the following text:\n\n{text}",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5
        )
        summary = response.choices[0].text.strip()
        return summary
    except Exception as e:
        return f"Error in generating summary: {str(e)}"

def generate_quiz_questions(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Generate ten quiz questions and answers from the following text:\n\n{text}",
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.5
        )
        quiz_questions = response.choices[0].text.strip()
        return quiz_questions
    except Exception as e:
        return f"Error in generating quiz questions: {str(e)}"

def process_youtube_link(url):
    transcript, error = get_transcript(url)
    if error:
        return error, ""

    summary = summarize_text(transcript)
    if "Error" in summary:
        return summary, ""

    quiz_questions = generate_quiz_questions(transcript)
    if "Error" in quiz_questions:
        return summary, quiz_questions

    return summary, quiz_questions

iface = gr.Interface(
    fn=process_youtube_link,
    inputs=gr.Textbox(label="YouTube URL", placeholder="Enter YouTube URL here..."),
    outputs=[
        gr.Textbox(label="Summary"),
        gr.Textbox(label="Quiz Questions")
    ],
    title="YouTube Summary and Quiz Generator",
    description="Enter a YouTube link to get a summary and quiz questions generated from the video's transcript."
)

if __name__ == "__main__":
    iface.launch()
