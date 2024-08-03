# AI-Powered Teaching Assistant

Welcome to the AI-Powered Teaching Assistant project! This project features three main bots: a Summary Bot, a Doubt Solving Bot, and a Quiz Generation Bot, all integrated into a cohesive website. This assistant is designed to help students by summarizing content, answering questions, and generating quizzes based on YouTube videos or uploaded media files.

[Project Link](https://deadshot1611.github.io/AI-powered-teaching-assistant/)

## Table of Contents
- [Project Overview and Architecture](#project-overview-and-architecture)
- [Setup and Installation Instructions](#setup-and-installation-instructions)
- [Usage Guide](#usage-guide)
  - [Summary Bot](#summary-bot)
  - [Doubt Solving Bot](#doubt-solving-bot)
  - [Quiz Generation Bot](#quiz-generation-bot)
- [API Documentation](#api-documentation)

## Project Overview and Architecture

This project utilizes several technologies:
- **Streamlit** for creating interactive web applications.
- **OpenAI API** for natural language processing and understanding.
- **YouTube Transcript API** for extracting transcripts from YouTube videos.
- **Pydub** for audio file manipulation.

The overall architecture of the project involves:
1. **Summary Bot**: Extracts and summarizes transcripts from YouTube videos or uploaded media files.
2. **Doubt Solving Bot**: Provides answers to user questions based on the transcript of a video or audio file.
3. **Quiz Generation Bot**: Generates quiz questions from the transcript of a video or audio file.

## Setup and Installation Instructions

To set up this project locally, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/Deadshot1611/AI-powered-teaching-assistant.git
    cd AI-powered-teaching-assistant
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the root directory.
    - Add your OpenAI API key to the `.env` file:
        ```env
        OPENAI_API_KEY=your_openai_api_key
        ```

5. Run the Streamlit application:
    ```sh
    streamlit run app.py
    ```

## Usage Guide

### Summary Bot

The Summary Bot extracts and summarizes transcripts from YouTube videos or uploaded media files.

#### Example Usage:
1. Choose the input type: YouTube URL or Upload audio/video file.
2. For YouTube URL, enter the video URL and click "Generate Summary".
3. For uploading a file, choose an audio or video file and click "Generate Summary".
4. The summary of the content will be displayed in a text area.

#### Brief Explanation:
- Uses the YouTube Transcript API to fetch video transcripts.
- Uses OpenAI's GPT-3.5-turbo for summarizing the fetched transcripts.

### Doubt Solving Bot

The Doubt Solving Bot answers user questions based on the transcript of a video or audio file.

#### Example Usage:
1. Choose the input type: YouTube URL or Upload audio/video file.
2. For YouTube URL, enter the video URL.
3. For uploading a file, choose an audio or video file.
4. Ask a question related to the content and click "Get Answer".
5. The bot will provide an answer based on the transcript.

#### Brief Explanation:
- Uses the same process as the Summary Bot to fetch transcripts.
- Uses OpenAI's GPT-3.5-turbo to answer questions based on the transcripts.

### Quiz Generation Bot

The Quiz Generation Bot generates quiz questions from the transcript of a video or audio file.

#### Example Usage:
1. Choose the input type: YouTube URL or Upload audio/video file.
2. For YouTube URL, enter the video URL.
3. For uploading a file, choose an audio or video file.
4. Click "Generate Quiz" to get quiz questions based on the content.

#### Brief Explanation:
- Follows the same process to fetch transcripts.
- Uses OpenAI's GPT-3.5-turbo to generate quiz questions from the transcript.

## API Documentation

- **YouTube Transcript API**: Used to fetch transcripts of YouTube videos.
- **OpenAI API**: Used for summarization, question answering, and quiz generation.
- **Pydub**: Used for converting and manipulating audio files for transcription.

For detailed implementation, please refer to the source code files in the repository.

Feel free to reach out if you have any questions or need further assistance.
