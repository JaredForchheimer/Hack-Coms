import os
import json
import re
import requests
import asl_translate
import sys
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi


from google import genai
from elevenlabs import ElevenLabs


with open("gemini_api_key.txt", "r") as f:
    client = genai.Client(api_key=f.read().strip())

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
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([entry["text"] for entry in transcript_list])
            return transcript_text.strip()
        except Exception as e:
            return f"Error fetching YouTube transcript: {str(e)}"

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
    """
    Moderates content using the Gemini 'text-moderation@latest' model via the SDK.
    Raises ValueError if content is flagged as unsafe.
    """
    # Call the API
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=content
    )

    if response.prompt_feedback and response.prompt_feedback.block_reason:
        return "Invalid"
    else:
        return content


def translate(content: str, target_language: str) -> str:
    """Translates text using the Gemini 'gemini-pro' model via the SDK."""
    translated = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="translate this text to " + target_language + " " + content,
    )
    if target_language == "ASL":
        asl_translate.make_vid(content)
        response = "ASL,video/output.mp4"
    else:
        path = text_to_speech(translated.text, "audio/translation.mp3", target_language)
        response = "Other," + path

    return response


def summarize(content: str) -> str:
    """Summarizes text using the Gemini 'gemini-pro' model via the SDK."""
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents="summarize this: " + content
    )

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
