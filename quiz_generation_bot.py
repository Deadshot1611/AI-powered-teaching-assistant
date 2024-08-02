import os
import io
import openai
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import logging
import warnings
from pydub import AudioSegment
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

def convert_to_supported_format(file):
    audio = AudioSegment.from_file(file)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)
    return buffer

def transcribe_audio(file):
    logging.info(f"Transcribing audio file")
    file = convert_to_supported_format(file)
    logging.info(f"Converted file to WAV format")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(file.getvalue())
        temp_file_path = temp_file.name

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with open(temp_file_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]
    except Exception as e:
        logging.error(f"Error in transcription: {str(e)}")
        return f"Error in transcription: {str(e)}"
    finally:
        os.remove(temp_file_path)

def summarize_text(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"Error in summarization: {str(e)}")
        return f"Error in summarization: {str(e)}"

def generate_quiz_questions(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates quiz questions. Your task is to generate ten quiz questions and four multiple choice answers for each question from the given text. It is CRUCIAL that you mark the correct answer with an asterisk (*) at the beginning of the answer line. There MUST be exactly one correct answer marked for each question. If you're unsure which answer is correct, mark the most likely correct answer. Use the following format for each question:\n\n1. Question\n   a) *Correct Answer\n   b) Incorrect Answer\n   c) Incorrect Answer\n   d) Incorrect Answer\n\n2. Question\n   a) Incorrect Answer\n   b) Incorrect Answer\n   c) *Correct Answer\n   d) Incorrect Answer\n\n..."},
                {"role": "user", "content": f"Generate quiz questions from the following text. Remember to mark EXACTLY ONE correct answer with an asterisk (*) for EACH question:\n\n{text}"}
            ],
            max_tokens=1500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"Error in quiz generation: {str(e)}")
        return f"Error in quiz generation: {str(e)}"

def generate_explanation(question, correct_answer, user_answer):
    try:
        prompt = f"Explain why the correct answer to the following question is '{correct_answer}' and not '{user_answer}':\n\n{question}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"Error in explanation generation: {str(e)}")
        return f"Error in explanation generation: {str(e)}"

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

def parse_quiz_questions(quiz_text):
    questions = []
    question_blocks = quiz_text.split("\n\n")
    for block in question_blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 5:
            question = lines[0].split(". ", 1)[1] if ". " in lines[0] else lines[0]
            choices = []
            correct_answer = None
            for line in lines[1:5]:
                if ") " in line:
                    choice = line.split(") ", 1)[1].strip()
                    if choice.startswith("*"):
                        correct_answer = choice[1:].strip()  # Remove the asterisk
                        choices.append(correct_answer)
                    else:
                        choices.append(choice)
            
            if not correct_answer:
                correct_answer = choices[0] if choices else "No correct answer provided"
            
            questions.append({
                "question": question,
                "choices": choices,
                "correct_answer": correct_answer
            })
    return questions

def check_answers(questions, user_answers):
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
            explanation = generate_explanation(question['question'], correct_answer, user_answer)
            feedback.append({
                "question": question['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "status": "Incorrect",
                "explanation": explanation
            })
    return feedback

def main():
    st.title("YouTube Transcript Quiz Generator")

    st.markdown("**Instructions:** Paste a YouTube link or upload a media file to generate a quiz.")

    option = st.selectbox("Choose input type", ("YouTube URL", "Upload audio/video file"))

    if "generated_quiz" not in st.session_state:
        st.session_state.generated_quiz = False
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "feedback" not in st.session_state:
        st.session_state.feedback = []
    if "url" not in st.session_state:
        st.session_state.url = ""
    if "transcript_text" not in st.session_state:
        st.session_state.transcript_text = ""

    if option == "YouTube URL":
        url = st.text_input("YouTube URL", value="")
        if url:
            st.session_state.url = url
            if st.button("Generate Quiz"):
                transcript_text = get_transcript(url)
                if "Error" not in transcript_text:
                    summary = summarize_text(transcript_text)
                    quiz_text = generate_quiz_questions(transcript_text)
                    questions = parse_quiz_questions(quiz_text)

                    st.session_state.questions = questions
                    st.session_state.user_answers = {}
                    st.session_state.generated_quiz = True
                    st.session_state.feedback = []
                    st.session_state.transcript_text = transcript_text

    elif option == "Upload audio/video file":
        uploaded_file = st.file_uploader("Choose an audio or video file", type=["mp3", "wav", "mp4", "mov"])
        if uploaded_file is not None:
            if st.button("Generate Quiz"):
                with st.spinner('Transcribing audio...'):
                    transcript_text = transcribe_audio(uploaded_file)
                if "Error" not in transcript_text:
                    summary = summarize_text(transcript_text)
                    quiz_text = generate_quiz_questions(transcript_text)
                    questions = parse_quiz_questions(quiz_text)
                    
                    # Check if all questions have valid correct answers
                    valid_questions = [q for q in questions if q['correct_answer'] != "No correct answer provided"]
                    
                    if len(valid_questions) < len(questions):
                        st.warning(f"Warning: {len(questions) - len(valid_questions)} questions did not have a marked correct answer. The first option was selected as the correct answer for these questions.")
                    
                    st.session_state.questions = valid_questions
                    st.session_state.user_answers = {}
                    st.session_state.generated_quiz = True
                    st.session_state.feedback = []
                    st.session_state.transcript_text = transcript_text

    if st.session_state.generated_quiz:
        st.write("## Summary")
        summary = summarize_text(st.session_state.transcript_text)
        st.write(summary)

        st.write("## Quiz Questions")
        form = st.form("quiz_form")
        for i, question in enumerate(st.session_state.questions):
            form.write(f"### Question {i+1}")
            form.write(question['question'])
            user_answer = form.selectbox(
                label="",
                options=question['choices'],
                key=f"question_{i+1}"
            )
            st.session_state.user_answers[f"question_{i+1}"] = user_answer

        submit_button = form.form_submit_button("Submit Answers")
        if submit_button:
            with st.spinner('Processing your answers...'):
                st.session_state.feedback = check_answers(st.session_state.questions, st.session_state.user_answers)
                st.write("## Feedback")
                for i, item in enumerate(st.session_state.feedback):
                    with st.expander(f"Question {i+1} Feedback"):
                        st.write(f"### {item['question']}")
                        st.write(f"**Your answer:** {item['user_answer']}")
                        st.write(f"**Correct answer:** {item['correct_answer']}")
                        if item['status'] == "Incorrect":
                            st.write(f"**Explanation:** {item['explanation']}")

if __name__ == "__main__":
    main()
