# AI-powered-teaching-assistant

Developer Log - May 28, 2024

Objective:
Develop a Gradio interface to generate a summary and quiz from YouTube video transcripts using OpenAI’s GPT-3.5-turbo model.

Steps Taken:

	1.	Environment Setup:
	•	Loaded OpenAI API key from .env file using dotenv.
	•	Installed necessary libraries: openai, gradio, youtube_transcript_api, re, and os.
	2.	Transcript Extraction:
	•	Utilized YouTubeTranscriptApi to fetch and concatenate video transcripts.
	3.	Summary Generation:
	•	Created a function to generate a summary of the transcript using OpenAI’s ChatCompletion.create method with gpt-3.5-turbo.
	4.	Quiz Question Generation:
	•	Implemented a function to generate ten quiz questions and four multiple-choice answers for each question from the transcript using OpenAI’s ChatCompletion.create method with gpt-3.5-turbo.
	5.	Parsing Quiz Questions:
	•	Developed a function to parse the generated quiz questions into a structured format.
	6.	Gradio Interface Development:
	•	Created a Gradio interface with the following components:
	•	Textbox for YouTube URL input.
	•	Textbox for displaying the summary.
	•	Textbox for displaying feedback.
	•	Ten Radio components for the quiz questions, initially hidden.
	•	Two Button components for generating the quiz and submitting answers.
	7.	Dynamic Content Handling:
	•	Used gr.update to dynamically update the visibility, labels, and choices of the quiz question components based on the generated quiz.
	8.	Answer Submission and Feedback:
	•	Implemented answer checking logic to provide feedback on the correctness of the user’s answers.
	9.	Troubleshooting:
	•	Addressed several issues during development, including:
	•	Ensuring the proper visibility and content update of quiz questions.
	•	Handling errors related to missing or incorrect arguments in function calls.
	•	Maintaining the state of the quiz questions for accurate answer checking.
 - Alex Ivory
