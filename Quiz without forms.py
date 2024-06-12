from openai import OpenAI

client = OpenAI(api_key=api_key)
import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi
import re
from dotenv import load_dotenv
import os

# Load the API key from.env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API key is not set. Please check your.env file and ensure OPENAI_API_KEY is set.")


def get_transcript(url):
    try:
        video_id = re.search(r"v=([^&]+)", url).group(1)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return str(e)

def summarize_text(text):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
    ],
    max_tokens=150)
    summary = response.choices[0].message.content.strip()
    return summary

def generate_quiz_questions(text):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Generate ten quiz questions and four multiple choice answers for each question from the following text:\n\n{text}"}
    ],
    max_tokens=1500)
    quiz_questions = response.choices[0].message.content.strip()
    return quiz_questions

def parse_quiz_questions(quiz_text):
    questions = []
    question_blocks = quiz_text.split("\n\n")
    for block in question_blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 5:
            question = lines[0]
            choices = lines[1:5]
            questions.append({"question": question, "choices": choices})
    return questions

def process_youtube_link(url):
    transcript = get_transcript(url)
    if "error" in transcript.lower():
        return "Error in fetching transcript: " + transcript, []

    summary = summarize_text(transcript)
    if "error" in summary.lower():
        return summary, []

    quiz_text = generate_quiz_questions(transcript)
    if "error" in quiz_text.lower():
        return summary, quiz_text

    questions = parse_quiz_questions(quiz_text)
    return summary, questions

def check_answers(questions, *user_answers):
    feedback = []
    correct_count = 0
    for i, question in enumerate(questions):
        correct_answer = question['choices'][0]  # Assuming first choice is correct
        user_answer = user_answers[i]
        if user_answer == correct_answer:
            feedback.append(f"Q{i+1}: Correct!")
            correct_count += 1
        else:
            feedback.append(f"Q{i+1}: Incorrect. The correct answer is: {correct_answer}")
    feedback.append(f"Your total score is {correct_count} out of {len(questions)}")
    return "\n".join(feedback)

def update_quiz(url):
    summary, questions = process_youtube_link(url)
    question_labels = []
    question_choices = []
    if questions:
        for q in questions:
            question_labels.append(q['question'])
            question_choices.append(q['choices'])
    return summary, question_labels, question_choices, questions

# Global state variable
global_questions_state = {}

def handle_quiz(url):
    global global_questions_state
    summary, question_labels, question_choices, questions = update_quiz(url)
    global_questions_state = questions  # Update the global state with the current questions
    updates = [gr.update(value=summary)] + [
        gr.update(visible=True, label=question_labels[i], choices=question_choices[i]) if i < len(question_labels) else gr.update(visible=False)
        for i in range(len(question_blocks))
    ]
    return updates

def handle_submit_answers(*answers):
    global global_questions_state
    feedback = check_answers(global_questions_state, *answers)
    return feedback

with gr.Blocks() as iface:
    url_input = gr.Textbox(label="YouTube URL", placeholder="Enter YouTube URL here...")
    summary_output = gr.Textbox(label="Summary", interactive=False)
    feedback_output = gr.Textbox(label="Feedback", lines=10, interactive=False)
    question_blocks = [gr.Radio(label=f"Question {i+1}", choices=["Option 1", "Option 2", "Option 3", "Option 4"], visible=False, interactive=True) for i in range(10)]

    submit_button = gr.Button("Generate Quiz")
    submit_button.click(fn=handle_quiz, inputs=url_input, outputs=[summary_output] + question_blocks)

    quiz_submit = gr.Button("Submit Answers")
    quiz_submit.click(fn=handle_submit_answers, inputs=question_blocks, outputs=feedback_output)

    gr.Markdown("# YouTube Summary and Quiz Generator")

iface.launch(share=True)
