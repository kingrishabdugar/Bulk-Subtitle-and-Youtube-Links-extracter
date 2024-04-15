import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Load the Excel file
df = pd.read_excel("urls.xlsx")

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    # Extract video ID from the URL
    video_id = row['url'].split('=')[-1]
    
    try:
        # Retrieve the available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Find the automatically generated transcript
        transcript = transcript_list.find_generated_transcript(['hi'])
        
        # Extract and concatenate the text
        plain_text = ""
        for segment in transcript.fetch():
            # Remove timestamps and HTML tags
            text = re.sub(r'<[^>]+>', '', segment['text'])
            plain_text += text + "..."
        
        # Prepend the title as a heading
        heading = f"Title: {row['title']}\n\n"
        plain_text = heading + plain_text

        # Define the file path
        file_path = f"FinalTrancriptions/{row['title']}.txt"
        
        # Write the plain text to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(plain_text)
        
        print(f"Transcript for '{row['title']}' saved to: {file_path}")
    
    except Exception as e:
        print(f"Error processing video '{row['title']}': {str(e)}")
