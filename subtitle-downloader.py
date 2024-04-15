from youtube_transcript_api import YouTubeTranscriptApi

# retrieve the available transcripts
transcript_list = YouTubeTranscriptApi.list_transcripts('PnPc2xDwMvQ')

# or automatically generated ones  
transcript = transcript_list.find_generated_transcript(['hi'])
print (transcript.fetch())
