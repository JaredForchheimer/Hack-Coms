# UniHear: A Multilingual + ASL News Translator

## Overview
UniHear is a multilingual and ASL (American Sign Language) translator designed to make global news accessible to everyone, regardless of language or hearing ability.  
It converts YouTube videos and online articles into ASL video translations, multilingual text summaries, and audio summaries in various languages.  
The platform is envisioned as a community-driven hub for inclusive, local, and global news sharing, powered by Gemini for profanity filtering to ensure safe, respectful content.

---

## Inspiration
Our inspiration stemmed from a simple observation: people connect most deeply with information in their own language.  
When our grandparents preferred the news in their native tongue, we realized that language carries emotion, culture, and comfort.  
Similarly, our conversations with members of the Deaf community revealed how traditional captions fail to capture nuance.  

This led us to ask:  
**What if everyone could access news in the form that felt most natural to them—whether through text, sound, or sign language?**

---

## What We Built
- ASL translation of videos for accessible visual comprehension  
- Multilingual text and audio summaries of online news and YouTube content  
- A Gemini-powered profanity filter to maintain inclusivity and trust  
- A JSON-based storage system for simplicity and efficiency  

---

## How We Built It
Development began in VS Code with GitHub for version control.  
After experimenting with Roo Code to generate the backend, we encountered several issues and decided to rewrite the backend manually.  
Using Claude and ChatGPT for debugging and refinement, we replaced Postgres with a JSON storage model for flexibility and reduced complexity.  
This combination of manual coding and AI-assisted improvement produced a stable prototype emphasizing reliability and accessibility.

---

## Lessons Learned
- AI accelerates development but cannot replace deliberate design or debugging.  
- Accessibility requires attention to cultural and linguistic nuances, not just translation accuracy.  
- Simplicity in storage and structure often leads to greater long-term maintainability.

---

## Challenges
1. Debugging AI-generated backend code and dependency conflicts  
2. Achieving realistic and expressive ASL video output  
3. Maintaining emotional and tonal consistency in multilingual summarization
   
---

## Folder Structure

```text
Hack-Coms/
│
├── app.py                     # Main application entry point
├── asl_translate.py           # ASL translation logic
├── elevenlabs_api_key.txt     # API key for ElevenLabs voice synthesis
├── gemini_api_key.txt         # API key for Gemini integration
├── INSTALL.md                 # Setup and installation instructions
├── main.py                    # Core backend logic
├── process.py                 # Processing module for media and text
├── requirements.txt           # Python dependencies
├── run.sh                     # Shell script to launch the app
├── stored_content.json        # Data and cache storage
├── todo.txt                   # Development notes
├── __init__.py                # Package initializer
│
└── .git/                      # Git version control metadata


---

## Tech Stack
- Python 3.10+  
- Gemini API for text moderation  
- ElevenLabs API for audio generation  
- JSON storage for lightweight data persistence  
- Git + GitHub for collaboration and version control  

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/UniHear.git
   cd UniHear
pip install -r requirements.txt
python app.py
bash run.sh
cd frontend
npm run dev
Open your browser at http://localhost:5000.
