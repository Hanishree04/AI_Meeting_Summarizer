# 🎙️ AI-Powered Meeting Summarizer

An AI-powered web application that converts meeting audio into text and generates concise summaries using Speech Recognition and Large Language Models (LLMs). The application also stores meeting records for future reference through an intuitive Gradio interface.

---

## Features

- 🎤 Upload or record meeting audio
- 📝 Automatic Speech-to-Text transcription using Whisper.cpp
- 🤖 AI-generated meeting summaries using Ollama Llama 3.2
- 📄 Display transcript and summary
- 💾 Store meeting history in MySQL
- 📥 Download transcript and summary
- 🌐 User-friendly Gradio interface

---

## Technologies Used

- Python
- Whisper.cpp
- Ollama Llama 3.2
- MySQL
- Gradio
---

##  Project Workflow

```text
Audio Upload / Recording
            │
            ▼
     Whisper.cpp
(Speech-to-Text Conversion)
            │
            ▼
      Transcript Generated
            │
            ▼
   Optional Context Input
            │
            ▼
     Ollama Llama 3.2
 (AI Summary Generation)
            │
            ▼
   Summary + Transcript
            │
            ▼
      MySQL Database
            │
            ▼
 Display & Download Results
```

---

## How It Works

1. Upload or record a meeting audio.
2. (Optional) Enter additional meeting context.
3. Click **Submit**.
4. Whisper.cpp converts speech into text.
5. Ollama Llama 3.2 analyzes the transcript and generates a concise summary.
6. The transcript and summary are displayed.
7. Results are stored in MySQL and can be viewed later through the History option.

---

## 📸 Application Interface

### Home Screen

<img width="1600" height="756" alt="WhatsApp Image 2026-05-08 at 9 59 53 AM" src="https://github.com/user-attachments/assets/6afb9348-66ff-47a8-a98f-a5d5fd3656a0" />


### Generated Transcript & Summary

<img width="1600" height="803" alt="WhatsApp Image 2026-05-02 at 12 30 44 PM" src="https://github.com/user-attachments/assets/905d1afa-6300-490c-ab30-172148b0ffe3" />


---

## Project Structure

```
AI-Powered-Meeting-Summarizer/
│── app.py
│── requirements.txt
│── README.md
│── database/
│── models/
│── images/
│── transcript/
│── summary/
└── utils/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/AI-Powered-Meeting-Summarizer.git
cd AI-Powered-Meeting-Summarizer
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start MySQL

Create a database and update the database credentials in the project.

### Pull Llama Model

```bash
ollama pull llama3.2
```

### Run the Application

```bash
python app.py
```

---

## Future Enhancements

- Multi-language transcription
- Speaker identification
- Action item extraction
- Sentiment analysis
- Cloud deployment
- Integration with Zoom, Google Meet, and Microsoft Teams

---

## Applications

- Business Meetings
- Online Classes
- Interviews
- Team Discussions
- Conferences
- Research Meetings

