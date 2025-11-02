import os
import json
import re
import requests
import asl_translate
import sys
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi


from google import genai


with open("gemini_api_key.txt", "r") as f:
    client = genai.Client(api_key=f.read().strip())


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
    if target_language == "ASL":
        asl_translate.make_vid(content)
        return "ASL,video/output.mp4"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Translate the following text into "
        + target_language
        + " :"
        + content,
    )

    return response.text


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
