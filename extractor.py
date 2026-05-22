import fitz
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


async def extract_pdf_text(file):
    contents = await file.read()

    with open("temp.pdf", "wb") as f:
        f.write(contents)

    doc = fitz.open("temp.pdf")
    text = ""

    for page in doc:
        text += page.get_text()

    return text


def extract_url_text(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def get_youtube_id(url):
    parsed = urlparse(url)

    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed.query).get("v", [None])[0]

    if parsed.hostname == "youtu.be":
        return parsed.path[1:]

    return None


def extract_youtube_text(url):
    video_id = get_youtube_id(url)

    if not video_id:
        return "Invalid YouTube URL"

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    return " ".join([item["text"] for item in transcript])