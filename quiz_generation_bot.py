import openai
from groq import Groq
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
from dotenv import load_dotenv
import os

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

def generate_quiz_questions(text):
    print("Debug: Generating quiz questions")  # Debug statement
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate ten quiz questions with four multiple choice answers each from the following text:\n\n{text}"}
            ],
            max_tokens=1500
        )
        print("Full Response (Quiz Questions):", response)  # Debug line to inspect the full response

        if response.choices and response.choices[0].message:
            quiz_questions = response.choices[0].message.content.strip()
            return quiz_questions
        else:
            return "No quiz questions available."
    except Exception as e:
        return f"Error in generating quiz questions: {str(e)}"

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

    quiz_text = generate_quiz_questions(transcript)
    if "error" in quiz_text.lower():
        return quiz_text, []

    questions = parse_quiz_questions(quiz_text)
    return questions

def check_answers(questions, user_answers):
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
    questions = process_youtube_link(url)
    return questions

st.title("YouTube Quiz Generator")

url_input = st.text_input("YouTube URL", placeholder="Enter YouTube URL here...")

if url_input:
    questions = update_quiz(url_input)
    if questions:
        st.write("### Quiz")
        user_answers = []
        for i, q in enumerate(questions):
            st.write(f"**{q['question']}**")
            user_answer = st.radio(f"Question {i+1}", q['choices'], key=i)
            user_answers.append(user_answer)

        if st.button("Submit Answers"):
            feedback = check_answers(questions, user_answers)
            st.write("### Feedback")
            st.write(feedback)
