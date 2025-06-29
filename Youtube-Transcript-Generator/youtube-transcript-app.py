import re
import requests
import streamlit as st
import json

def get_youtube_transcript(video_id):
    try:
        # Step 1: Send an HTTP GET request to the YouTube video page
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        response = requests.get(video_url)
        response.raise_for_status()  # Ensure the request was successful

        # Log the response snippet for debugging
        #st.text_area("Video Page Response Snippet", response.text, height=300)

        # Step 2: Extract captionTracks JSON from the response text
        caption_tracks_match = re.search(r'"captionTracks":(\[.*?\])', response.text)
        if not caption_tracks_match:
            raise ValueError("Could not find caption tracks in the video page.")

        caption_tracks_json = caption_tracks_match.group(1)
        caption_tracks = json.loads(caption_tracks_json)

        # Log the extracted caption tracks for debugging
        #st.text_area("Extracted Caption Tracks", json.dumps(caption_tracks, indent=2), height=300)

        # Return the available caption tracks
        return caption_tracks

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_transcript(url):
    try:
        # Replace \u0026 with & in the URL
        subtitle_url = url.replace("\\u0026", "&")

        # Log the subtitle URL for debugging
        #st.text_area("Generated Subtitle URL", subtitle_url, height=100)

        # Step 3: Send a GET request to the subtitle URL to retrieve the transcript (XML format)
        subtitle_response = requests.get(subtitle_url)
        subtitle_response.raise_for_status()

        # Log the subtitle XML response for debugging
        #st.text_area("Subtitle XML Response", subtitle_response.text, height=300)

        return subtitle_response.text

    except Exception as e:
        st.error(f"An error occurred while fetching the transcript: {e}")
        return ""

def parse_transcript(xml_content):
    try:
        # Extract timed and plain texts from XML content
        timed_texts = re.findall(r'<text start="(.*?)" dur="(.*?)">(.*?)<\/text>', xml_content)
        joined_texts = " ".join([text[2] for text in timed_texts])

        # Log the parsed texts for debugging
        #st.text_area("Parsed Timed Texts (Sample)", str(timed_texts[:10]), height=150)  # Show first 10 as a sample
        #st.text_area("Joined Text", joined_texts, height=300)

        return timed_texts, joined_texts
    except Exception as e:
        st.error(f"An error occurred while parsing the transcript: {e}")
        return [], ""

# Streamlit app
st.title("YouTube Transcript Extractor")
st.markdown("### Extract subtitles from YouTube videos in multiple languages!")

video_url = st.text_input("Enter YouTube Video URL:")

if st.button("Fetch Available Languages"):
    if video_url:
        # Extract video ID from the YouTube URL
        video_id_match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", video_url)
        if video_id_match:
            video_id = video_id_match.group(1)

            # Get available caption tracks
            caption_tracks = get_youtube_transcript(video_id)

            if caption_tracks:
                # Populate language options
                language_options = {track['languageCode']: track['baseUrl'] for track in caption_tracks}
                st.session_state['language_options'] = language_options
                st.success("Languages fetched successfully! Select a language from the dropdown below.")
        else:
            st.error("Invalid YouTube URL. Please enter a valid one.")
    else:
        st.error("Please enter a YouTube video URL.")

if 'language_options' in st.session_state:
    language_code = st.selectbox("Select Language:", st.session_state['language_options'].keys())

    if st.button("Get Transcript"):
        if language_code:
            transcript_url = st.session_state['language_options'][language_code]

            # Fetch transcript XML
            transcript_xml = fetch_transcript(transcript_url)
            if "<transcript>" in transcript_xml:
                timed_texts, joined_texts = parse_transcript(transcript_xml)

                # Display results
                st.subheader("Timed Texts")
                st.text_area("Timed Texts", str(timed_texts), height=300)

                st.subheader("Joined Text")
                st.text_area("Joined Text", joined_texts, height=300)

                # Provide download option
                st.download_button(
                    label="Download Full Transcript",
                    data=joined_texts,
                    file_name="transcript.txt",
                    mime="text/plain"
                )
            else:
                st.error("Could not retrieve transcript.")
        else:
            st.error("Please select a language.")
