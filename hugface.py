import streamlit as st
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
import re
import tempfile
import os
from transformers import pipeline
import soundfile as sf

# Initialize the pipeline with the model
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")

# Function to transcribe audio using Hugging Face Whisper
def transcribe_audio(file_path):
    # Load audio file into NumPy array
    audio_input, _ = sf.read(file_path)
    transcription = pipe(audio_input)["text"]
    return transcription

# Function to get YouTube transcript
def get_transcript(url):
    try:
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if video_id_match:
            video_id = video_id_match.group(1)
        else:
            return "Error: Invalid YouTube URL"

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return str(e)

# Function to summarize text using OpenAI API
def summarize_text(client, text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ]
    )
    summary = response.choices[0].message.content.strip()
    return summary

# Function to generate quiz questions using OpenAI API
def generate_quiz_questions(client, text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate ten quiz questions and four multiple choice answers for each question from the following text. Mark the correct answer with an asterisk (*) at the beginning:\n\n{text}"}
        ]
    )
    quiz_questions = response.choices[0].message.content.strip()
    return quiz_questions

# Function to parse quiz questions
def parse_quiz_questions(quiz_text):
    questions = []
    question_blocks = quiz_text.split("\n\n")
    for block in question_blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 5:
            question = lines[0]
            choices = [line.replace('*', '').strip() for line in lines[1:5]]
            correct_answer_lines = [line for line in lines[1:5] if '*' in line]
            if correct_answer_lines:
                correct_answer = correct_answer_lines[0].replace('*', '').strip()
            else:
                correct_answer = "No correct answer provided"
            questions.append({"question": question, "choices": choices, "correct_answer": correct_answer})
    return questions

# Function to generate explanation using OpenAI API
def generate_explanation(client, question, correct_answer, user_answer):
    prompt = f"Explain why the correct answer to the following question is '{correct_answer}' and not '{user_answer}':\n\n{question}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    explanation = response.choices[0].message.content.strip()
    return explanation

# Function to check answers and provide feedback
def check_answers(client, questions, user_answers):
    feedback = []
    correct_count = 0
    for i, question in enumerate(questions):
        correct_answer = question['correct_answer']
        user_answer = user_answers.get(f"question_{i+1}", "")
        if user_answer == correct_answer:
            feedback.append({
                "question": question['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "status": "Correct"
            })
            correct_count += 1
        else:
            explanation = generate_explanation(client, question['question'], correct_answer, user_answer)
            feedback.append({
                "question": question['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "status": "Incorrect",
                "explanation": explanation
            })
    return feedback

# Function to handle uploaded file
def handle_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    return tmp_file_path

# Streamlit UI
st.title("YouTube Transcript Quiz Generator")

st.markdown("**Instructions:** Enter your OpenAI API key and paste a YouTube link or upload a media file to generate a quiz.")

api_key = st.text_input("Enter your OpenAI API Key", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

option = st.selectbox("Choose input type", ("YouTube URL", "Upload audio/video file"))

if "generated_quiz" not in st.session_state:
    st.session_state.generated_quiz = False

if option == "YouTube URL":
    url = st.text_input("YouTube URL", value="")
    if api_key and url:
        if st.button("Generate Quiz"):
            transcript_text = get_transcript(url)
            if "Error" not in transcript_text:
                summary = summarize_text(client, transcript_text)
                quiz_text = generate_quiz_questions(client, transcript_text)
                questions = parse_quiz_questions(quiz_text)

                st.session_state.summary = summary
                st.session_state.questions = questions
                st.session_state.user_answers = {}
                st.session_state.generated_quiz = True

if option == "Upload audio/video file":
    uploaded_file = st.file_uploader("Choose an audio or video file", type=["mp3", "wav", "mp4", "mov"])
    if uploaded_file and api_key:
        if st.button("Generate Quiz"):
            tmp_file_path = handle_uploaded_file(uploaded_file)
            with st.spinner('Transcribing audio...'):
                transcript_text = transcribe_audio(tmp_file_path)
            os.remove(tmp_file_path)
            if "Error" not in transcript_text:
                summary = summarize_text(client, transcript_text)
                quiz_text = generate_quiz_questions(client, transcript_text)
                questions = parse_quiz_questions(quiz_text)

                st.session_state.summary = summary
                st.session_state.questions = questions
                st.session_state.user_answers = {}
                st.session_state.generated_quiz = True

if st.session_state.generated_quiz:
    st.write("## Summary")
    st.write(st.session_state.summary)

    st.write("## Quiz Questions")
    for i, question in enumerate(st.session_state.questions):
        st.write(f"### Question {i+1}")
        st.write(question['question'])
        st.session_state.user_answers[f"question_{i+1}"] = st.radio(
            label="",
            options=question['choices'],
            key=f"question_{i+1}"
        )

    if st.button("Submit Answers"):
        if "questions" in st.session_state and st.session_state.questions:
            with st.spinner('Processing your answers...'):
                feedback = check_answers(client, st.session_state.questions, st.session_state.user_answers)
                st.write("## Feedback")
                for i, item in enumerate(feedback):
                    with st.expander(f"Question {i+1} Feedback"):
                        st.write(f"### {item['question']}")
                        st.write(f"**Your answer:** {item['user_answer']}")
                        st.write(f"**Correct answer:** {item['correct_answer']}")
                        if item['status'] == "Incorrect":
                            st.write(f"**Explanation:** {item['explanation']}")
        else:
            st.write("Please generate the quiz first.")
