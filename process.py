import os
import json
import re
import requests
import asl_translate
import sys
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
import yt_dlp
import shutil
#  from youtube_transcript_api import YouTubeTranscriptApi


import google.generativeai as genai
from elevenlabs import ElevenLabs


with open("gemini_api_key.txt", "r") as f:
    genai.configure(api_key=f.read().strip())

with open("elevenlabs_api_key.txt", "r") as f:
    elevenlabs_client = ElevenLabs(api_key=f.read().strip())


def scrape(url: str) -> str:
    """Scrapes text content from a website or a YouTube transcript."""
    youtube_match = re.match(
        r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([\w-]+)", url
    )
    if youtube_match:
        video_id = youtube_match.group(4)
        print(f"Fetching YouTube transcript for video ID: {video_id}...")
        try:
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'subtitlesformat': 'json3',
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Try to get subtitles
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # Prefer manual subtitles over auto-generated
                if 'en' in subtitles:
                    subtitle_data = subtitles['en']
                elif 'en' in automatic_captions:
                    subtitle_data = automatic_captions['en']
                else:
                    # No English subs, try any language
                    all_subs = {**subtitles, **automatic_captions}
                    if all_subs:
                        first_lang = list(all_subs.keys())[0]
                        subtitle_data = all_subs[first_lang]
                    else:
                        raise ValueError("No subtitles available")
                
                # Find json3 format
                json3_url = None
                for fmt in subtitle_data:
                    if fmt.get('ext') == 'json3':
                        json3_url = fmt.get('url')
                        break
                
                if json3_url:
                    # Fetch and parse the subtitle data
                    response = requests.get(json3_url)
                    subtitle_json = response.json()
                    
                    # Extract text from events
                    transcript_text = []
                    for event in subtitle_json.get('events', []):
                        if 'segs' in event:
                            for seg in event['segs']:
                                if 'utf8' in seg:
                                    transcript_text.append(seg['utf8'])
                    
                    result = ' '.join(transcript_text).strip()
                    print(f"Successfully fetched transcript: {len(result)} characters")
                    return result
                else:
                    raise ValueError("Could not find suitable subtitle format")
                    
        except Exception as e:
            print(f"YouTube transcript error: {str(e)}")
            # Fallback to video description
            try:
                print("Attempting to get video description...")
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', '')
                    description = info.get('description', '')
                    content = f"Title: {title}\n\nDescription: {description}"
                    if content.strip():
                        print("Using video title and description")
                        return content
                    else:
                        return "Error: No transcript or description available for this video."
            except Exception as e2:
                return f"Error: Could not extract any content from YouTube video: {str(e2)}"

    # Rest of your website scraping code...
    print(f"Fetching website content from: {url}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        texts = []
        for tag in soup.find_all(["p", "h1", "h2", "h3", "article", "main"]):
            texts.append(tag.get_text(strip=True))

        content = "\n".join(texts)
        if not content:
            return "Error: No text content found using common tags."
        return content
    except Exception as e:
        return f"Error fetching website content: {str(e)}"

def parse(content: str) -> str:
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(content)
        
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            raise ValueError("Content was blocked by safety filters")
        else:
            return content
    except Exception as e:
        raise ValueError(f"Error parsing content: {str(e)}")


def translate(content: str, target_language: str, url: str = "") -> str:
    """Translates text using the Gemini 'gemini-pro' model via the SDK."""
    
    # Generate unique filename based on URL hash or timestamp
    unique_id = hashlib.md5(url.encode()).hexdigest()[:10] if url else datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if target_language == "ASL":
        try:
            asl_translate.make_vid(content)
            source_path = "video/output.mp4"
            video_path = f"video/output_{unique_id}.mp4"
            os.makedirs("video", exist_ok=True)

            if os.path.exists(source_path):
                shutil.copy(source_path, video_path)
            else:
                raise FileNotFoundError(f"ASL video not generated at {source_path}")

            response = f"ASL,{video_path},ASL,{content}"  # Add the 4th part
        except Exception as e:
            print(f"Error generating ASL video: {str(e)}")
            raise
    else:
        # For other languages, translate the text first
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        translated = model.generate_content(
            f"Translate the following text to {target_language}. Provide only the direct translation without any additional options, notes, or explanations:\n\n{content}"
        )
        
        translated_text = translated.text  # Store the translated text
        
        # Ensure audio directory exists
        os.makedirs("audio", exist_ok=True)
        
        audio_path = f"audio/translation_{target_language}_{unique_id}.mp3"
        path = text_to_speech(translated_text, audio_path, target_language)  # Use translated_text
        
        # Return with 4 parts including the translated text
        response = f"Other,{path},{target_language},{translated_text}"

    return response


def summarize(content: str) -> str:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("summarize this: " + content)
    return response.text


def load_storage(file_path="stored_content.json") -> dict:
    """Loads a dictionary from a JSON file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_storage(data: dict, file_path="stored_content.json"):
    """Saves a dictionary to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def text_to_speech(text: str, output_path: str, language: str = "en") -> str:
    """
    Converts text to speech using ElevenLabs API and saves to file.
    Returns the path to the saved audio file.
    """
    try:
        # Map common language names to voice IDs (you can customize these)
        # Using multilingual v2 model which supports multiple languages
        voice_map = {
            "spanish": "pNInz6obpgDQGcFmaJgB",  # Adam (multilingual)
            "french": "pNInz6obpgDQGcFmaJgB",
            "german": "pNInz6obpgDQGcFmaJgB",
            "italian": "pNInz6obpgDQGcFmaJgB",
            "portuguese": "pNInz6obpgDQGcFmaJgB",
            "polish": "pNInz6obpgDQGcFmaJgB",
            "hindi": "pNInz6obpgDQGcFmaJgB",
            "default": "pNInz6obpgDQGcFmaJgB",  # Default multilingual voice
        }

        voice_id = voice_map.get(language.lower(), voice_map["default"])

        print(f"Generating speech for {language}...")

        # Generate audio using the new SDK
        audio_generator = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
        )

        # Save the audio to file
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)

        print(f"Audio saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        raise
