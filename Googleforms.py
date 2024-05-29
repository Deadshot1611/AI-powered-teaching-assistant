import openai
import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi
import re
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load the API key from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API key is not set. Please check your .env file and ensure OPENAI_API_KEY is set.")

openai.api_key = api_key

# Path to your service account key file
SERVICE_ACCOUNT_FILE = '/Users/alexanderivory/Another Alex Storage Dropbox/Alexander Ivory/Mac/Documents/100X/AI-powered-teaching-assistant/teaching-assistant-424718-869fd40a1a26.json'
SCOPES = ['https://www.googleapis.com/auth/forms.body']

# Authenticate and initialize the API client
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('forms', 'v1', credentials=credentials)

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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
            ]
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except Exception as e:
        return str(e)

def generate_quiz_questions(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate ten quiz questions and four multiple choice answers for each question from the following text:\n\n{text}"}
            ]
        )
        quiz_questions = response['choices'][0]['message']['content'].strip()
        return quiz_questions
    except Exception as e:
        return str(e)

def create_google_form(quiz_title, questions):
    # Create the form with title only
    form = {
        "info": {
            "title": quiz_title,
        }
    }
    
    created_form = service.forms().create(body=form).execute()
    form_id = created_form['formId']
    
    # Prepare batch update request to add questions
    requests = []
    for i, question in enumerate(questions, start=1):
        requests.append({
            "createItem": {
                "item": {
                    "title": f"Q{i}. {question['question']}",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [{"value": option} for option in question['choices']],
                                "shuffle": False
                            }
                        }
                    }
                },
                "location": {
                    "index": i - 1
                }
            }
        })
    
    batch_update_request = {
        "requests": requests
    }
    
    # Batch update the form to add questions
    service.forms().batchUpdate(formId=form_id, body=batch_update_request).execute()
    return created_form['responderUri']

def generate_google_form_from_quiz(title, quiz_questions):
    # Extract questions and choices from the quiz text
    questions = []
    for q in quiz_questions.split("\n\n"):
        parts = q.split("\n")
        if len(parts) > 4:  # Ensure there are exactly 4 choices
            question = parts[0]
            choices = parts[1:5]
            questions.append({"question": question, "choices": choices})
    
    return create_google_form(title, questions)

def process_youtube_link(url):
    transcript = get_transcript(url)
    if "error" in transcript.lower():
        return "Error in fetching transcript: " + transcript, "", ""

    summary = summarize_text(transcript)
    if "error" in summary.lower():
        return summary, "", ""

    quiz_questions = generate_quiz_questions(transcript)
    if "error" in quiz_questions.lower():
        return summary, quiz_questions, ""

    form_link = generate_google_form_from_quiz("Generated Quiz", quiz_questions)
    iframe = f'<iframe src="{form_link}" width="100%" height="500"></iframe>'
    return summary, form_link, iframe

iface = gr.Interface(
    fn=process_youtube_link,
    inputs=gr.Textbox(label="YouTube URL", placeholder="Enter YouTube URL here..."),
    outputs=[
        gr.Textbox(label="Summary"),
        gr.Textbox(label="Google Form Link"),
        gr.HTML(label="Google Form")
    ],
    title="YouTube Summary and Quiz Generator",
    description="Enter a YouTube link to get a summary and a Google Form quiz generated from the video's transcript."
)

if __name__ == "__main__":
    iface.launch()
