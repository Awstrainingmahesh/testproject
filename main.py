import streamlit as st
import yt_dlp
import whisper
from transformers import pipeline
import os
import re
from pydub import AudioSegment

# Function to extract video ID from URL
def get_video_id(url):
    match = re.search(r"v=([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else None

# Function to download YouTube audio
def download_audio(video_url):
    ydl_opts = {
        "format": "m4a/bestaudio",
        "outtmpl": "audio.m4a",
        "nocheckcertificate": True,
        "quiet": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.youtube.com/",
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            audio_path = "audio.m4a"

            if not os.path.exists(audio_path):
                return None

            sound = AudioSegment.from_file(audio_path, format="m4a")
            sound.export("audio.mp3", format="mp3")

            return "audio.mp3"
        except Exception as e:
            st.error(f"Error downloading audio: {e}")
            return None

# Function to transcribe audio using Whisper
def transcribe_audio(audio_path):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path)
    return result["text"]

# Function to split text into chunks
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# Function to summarize text
def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = chunk_text(text, chunk_size=500)
    summaries = []

    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summaries.append(summary[0]["summary_text"])
        except Exception:
            summaries.append(chunk)

    final_summary = " ".join(summaries)
    if len(final_summary.split()) > 500:
        final_summary = summarizer(final_summary, max_length=200, min_length=50, do_sample=False)[0]["summary_text"]
    
    return final_summary

# Streamlit App
st.title("📹 YouTube Video Summarizer")
st.write("Enter a YouTube video URL to generate a summary.")

video_url = st.text_input("Enter YouTube Video URL:")

if st.button("Summarize Video"):
    if not video_url:
        st.warning("Please enter a valid YouTube URL.")
    else:
        st.info("🔄 Downloading audio...")
        audio_path = download_audio(video_url)

        if not audio_path:
            st.error("❌ Failed to download audio. Try another video.")
        else:
            st.info("📝 Transcribing audio...")
            transcript = transcribe_audio(audio_path)

            if not transcript.strip():
                st.error("❌ Failed to transcribe audio.")
            else:
                st.success("✅ Transcription Complete!")
                st.text_area("🗒 Full Transcript:", transcript, height=200)

                st.info("📜 Summarizing transcript...")
                summary = summarize_text(transcript)
                
                st.success("✅ Summary Generated!")
                st.text_area("📄 Video Summary:", summary, height=150)
