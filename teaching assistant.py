import os
from openai import OpenAI

# Set your OpenAI API key in an environment variable and access it here
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi
import re

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

        return output
    except Exception as e:
        return str(e)

def summarize_text(text):
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
        ])
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        return str(e)

def generate_quiz_questions(text):
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate ten quiz questions and answers from the following text:\n\n{text}"}
        ])
        quiz_questions = response.choices[0].message.content.strip()
        return quiz_questions
    except Exception as e:
        return str(e)

def process_youtube_link(url):
    transcript = get_transcript(url)
    if "error" in transcript.lower():
        return "Error in fetching transcript: " + transcript, ""
    summary = summarize_text(transcript)
    if "error" in summary.lower():
        return summary, ""
    quiz_questions = generate_quiz_questions(transcript)
    if "error" in quiz_questions.lower():
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
    iface.launch()