import re
import requests
import streamlit as st
import json
from bs4 import BeautifulSoup

# Helper Function: Fetch HTML Content
def fetch_html(video_url):
    try:
        response = requests.get(video_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching video page: {e}")
        return None

# Feature 1: Extract Video Metadata
def extract_video_metadata(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title_tag = soup.find("meta", property="og:title")
        description_tag = soup.find("meta", property="og:description")
        published_date_tag = soup.find("meta", itemprop="datePublished")
        channel_name_tag = soup.find("meta", itemprop="author")
        
        # Safely extract content only if the tag is found
        title = title_tag['content'] if title_tag else "No title found"
        description = description_tag['content'] if description_tag else "No description found"
        published_date = published_date_tag['content'] if published_date_tag else "No publish date found"
        channel_name = channel_name_tag['content'] if channel_name_tag else "No channel name found"
        
        print(title, description, published_date, channel_name)
        return {
            "title": title,
            "description": description,
            "published_date": published_date,
            "channel_name": channel_name
        }
    except Exception as e:
        st.error(f"Error extracting video metadata: {e}")
        return {}

# Feature 2: Extract Engagement Metrics
def extract_engagement_metrics(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.find_all("script")
        for script in scripts:
            if "viewCount" in script.text:
                match = re.search(r'"viewCount":"(\d+)","likeCount":"(\d+)"', script.text)
                if match:
                    return {
                        "views": match.group(1),
                        "likes": match.group(2)
                    }
        return {"views": "N/A", "likes": "N/A"}
    except Exception as e:
        st.error(f"Error extracting engagement metrics: {e}")
        return {}

# Feature 3: Extract Comments (Simplified)
def extract_comments(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.find_all("script")
        for script in scripts:
            if "continuation" in script.text:
                match = re.search(r'"continuation":"([^"]+)"', script.text)
                if match:
                    return f"Comments Continuation Token: {match.group(1)} (Further handling required)"
        return "Comments feature needs API access."
    except Exception as e:
        st.error(f"Error extracting comments: {e}")
        return "Error fetching comments."

# Feature 4: Extract Related Videos
def extract_related_videos(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        related_videos = []
        for video in soup.select("a#thumbnail"):
            title = video.get("title")
            link = f"https://www.youtube.com{video.get('href')}"
            if title and link:
                related_videos.append({"title": title, "link": link})
        return related_videos
    except Exception as e:
        st.error(f"Error extracting related videos: {e}")
        return []

# Streamlit UI
st.title("YouTube Video Data Extractor")
st.markdown("### Extract metadata, engagement metrics, comments, and more from YouTube videos!")

video_url = st.text_input("Enter YouTube Video URL:")

if st.button("Extract Video Data"):
    if video_url:
        # Step 1: Fetch HTML Content
        html_content = fetch_html(video_url)
        if html_content:
            # Step 2: Extract Metadata
            metadata = extract_video_metadata(html_content)
            if metadata:
                st.subheader("Video Metadata")
                st.json(metadata)

            # Step 3: Extract Engagement Metrics
            engagement_metrics = extract_engagement_metrics(html_content)
            if engagement_metrics:
                st.subheader("Engagement Metrics")
                st.json(engagement_metrics)

            # Step 4: Extract Comments (Simplified)
            #comments = extract_comments(html_content)
            #st.subheader("Comments")
            #st.text(comments)

            # Step 5: Extract Related Videos
            related_videos = extract_related_videos(html_content)
            if related_videos:
                st.subheader("Related Videos")
                for video in related_videos[:10]:  # Show top 10 related videos
                    st.markdown(f"[{video['title']}]({video['link']})")
    else:
        st.error("Please enter a valid YouTube URL.")
