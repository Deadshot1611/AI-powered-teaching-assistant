### YouTube Transcript Quiz Generator

This script fetches the transcript of a YouTube video, generates a summary, and creates a quiz with multiple-choice questions based on the video's content. Users can then take the quiz, submit their answers, and receive feedback on their performance.

### Features
1. **Fetch YouTube Transcript**: Given a YouTube URL, the script extracts the video's transcript using the `youtube_transcript_api`.
2. **Generate Summary**: The script uses OpenAI's GPT-3.5-turbo model to generate a concise summary of the transcript.
3. **Create Quiz Questions**: It generates multiple-choice quiz questions based on the transcript.
4. **Interactive Quiz**: Users can take the quiz directly on a Streamlit interface, select answers, and submit them.
5. **Feedback**: After submission, the script provides feedback on the user's performance, indicating the correct answers.

### How to Run the Script

#### Prerequisites
1. **Python**: Make sure Python is installed on your machine.
2. **OpenAI API Key**: Sign up on [OpenAI](https://platform.openai.com/signup) to get your API key.
3. **YouTube API**: The script uses `youtube_transcript_api` to fetch the transcript from YouTube.

#### Setup Instructions

1. **Clone the Repository**: Clone the repository from GitHub to your local machine.
   ```sh
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Install Dependencies**: Install the required Python packages using `pip`.
   ```sh
   pip install -r requirements.txt
   ```

3. **Environment Variables**: Create a `.env` file in the root directory of the project and add your OpenAI API key.
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the Script**: Execute the script using Streamlit.
   ```sh
   streamlit run streamlit_quiz.py
   ```

### Script Explanation

Here’s a brief overview of the script's main functions:

1. **get_transcript(url)**:
   - Extracts the video ID from the YouTube URL.
   - Fetches the transcript using the `YouTubeTranscriptApi`.
   - Returns the transcript as a string.

2. **summarize_text(text)**:
   - Uses OpenAI's GPT-3.5-turbo model to generate a summary of the provided text.
   - Returns the summary.

3. **generate_quiz_questions(text)**:
   - Uses OpenAI's GPT-3.5-turbo model to generate ten quiz questions and four multiple-choice answers for each question from the provided text.
   - Returns the quiz questions as a string.

4. **parse_quiz_questions(quiz_text)**:
   - Parses the quiz questions and answers from the generated text.
   - Extracts the correct answer by identifying the line with an asterisk (*).
   - Returns a list of questions with their choices and correct answers.

5. **check_answers(questions, user_answers)**:
   - Checks the user's answers against the correct answers.
   - Provides feedback for each question.
   - Calculates the user's score.
   - Returns the feedback and score.

6. **Streamlit Interface**:
   - Displays the YouTube URL input box.
   - Shows the generated summary.
   - Displays the quiz questions with multiple-choice options.
   - Provides a submit button for users to submit their answers.
   - Displays feedback after submission.

By following these instructions, users can set up and run the YouTube Transcript Quiz Generator script on their local machine using Streamlit. This script provides an interactive way to test comprehension of YouTube video content through automatically generated quizzes.
