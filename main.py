import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube
import speech_recognition as sr
from transformers import pipeline
from textblob import TextBlob
import re

# Function to download audio from YouTube
def download_audio(url):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    return audio_stream.download()

# Function to convert speech to text
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    return text

# Function to summarize text
def summarize_text(text, max_length=50000):
    summarization_pipeline = pipeline("summarization")
    summary = summarization_pipeline(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

# Main Streamlit app
def main():
    st.title("YouTube Video Summarizer")

    # User input for YouTube video URL
    video_url = st.text_input("Enter YouTube Video URL:", "")

    # User customization options
    max_summary_length = st.slider("Max Summary Length:", 1000, 20000, 50000)

    if st.button("Summarize"):
        try:
            # Download audio from YouTube video
            audio_file = download_audio(video_url)

            # Convert speech to text and
            video_text = speech_to_text(audio_file)

            # Summarize the transcript
            summary = summarize_text(video_text, max_length=max_summary_length)

            # Display summarized text
            st.subheader("Video Summary:")
            st.write(summary)

        except TranscriptsDisabled:
            st.error("Transcripts are disabled for this video.")
        except NoTranscriptFound:
            st.error("No transcript found for this video.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
