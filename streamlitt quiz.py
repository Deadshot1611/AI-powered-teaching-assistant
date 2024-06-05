import openai
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import whisper
import tempfile
import os

def transcribe_audio(file_path):
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

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

def summarize_text(api_key, text):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        max_tokens=150
    )
    summary = response.choices[0]['message']['content'].strip()
    return summary

def generate_quiz_questions(api_key, text):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate ten quiz questions and four multiple choice answers for each question from the following text. Mark the correct answer with an asterisk (*) at the beginning:\n\n{text}"}
        ],
        max_tokens=300
    )
    quiz_questions = response.choices[0]['message']['content'].strip()
    return quiz_questions

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

def generate_explanation(api_key, question, correct_answer, user_answer):
    openai.api_key = api_key
    prompt = f"Explain why the correct answer to the following question is '{correct_answer}' and not '{user_answer}':\n\n{question}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    explanation = response.choices[0]['message']['content'].strip()
    return explanation

def check_answers(api_key, questions, user_answers):
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
            explanation = generate_explanation(api_key, question['question'], correct_answer, user_answer)
            feedback.append({
                "question": question['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "status": "Incorrect",
                "explanation": explanation
            })
    return feedback

def handle_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    return tmp_file_path

st.title("YouTube Transcript Quiz Generator")

st.markdown("**Instructions:** Enter your OpenAI API key and paste a YouTube link or upload a media file to generate a quiz.")

api_key = st.text_input("Enter your OpenAI API Key", type="password")
option = st.selectbox("Choose input type", ("YouTube URL", "Upload audio/video file"))

if "generated_quiz" not in st.session_state:
    st.session_state.generated_quiz = False

if option == "YouTube URL":
    url = st.text_input("YouTube URL", value="")
    if api_key and url:
        if st.button("Generate Quiz"):
            transcript_text = get_transcript(url)
            if "Error" not in transcript_text:
                summary = summarize_text(api_key, transcript_text)
                quiz_text = generate_quiz_questions(api_key, transcript_text)
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
            transcript_text = transcribe_audio(tmp_file_path)
            os.remove(tmp_file_path)
            if "Error" not in transcript_text:
                summary = summarize_text(api_key, transcript_text)
                quiz_text = generate_quiz_questions(api_key, transcript_text)
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
                feedback = check_answers(api_key, st.session_state.questions, st.session_state.user_answers)
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
