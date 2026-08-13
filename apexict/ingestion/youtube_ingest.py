import yt_dlp
import os
import json
import glob
from typing import Dict, Any, List
from apexict.processing.caption_cleaner import ICTCaptionCleaner
from apexict.processing.chunker import TranscriptChunker

def date_filter(info, *, incomplete):
    upload_date = info.get('upload_date')
    if upload_date and upload_date < '20240101':
        return 'Video is older than Jan 1, 2024'
    return None

class YouTubeIngestionPipeline:
    def __init__(self):
        self.cleaner = ICTCaptionCleaner()
        self.chunker = TranscriptChunker(chunk_duration_seconds=30)
        
        self.temp_dir = "temp_subs"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.ydl_opts = {
            'quiet': True,
            'skip_download': True,           
            'writesubtitles': True,          
            'writeautomaticsub': True,       
            'subtitleslangs': ['en', 'en-US', 'en-GB', 'en.*'], 
            'subtitlesformat': 'json3',      
            'outtmpl': f'{self.temp_dir}/%(id)s.%(ext)s',     
            'match_filter': date_filter
        }

    def process_video(self, video_url: str) -> Dict[str, Any]:
        video_id = video_url.split("v=")[-1].split("&")[0]
        print(f"[Ingestion] Fetching metadata & transcript for: {video_id}")
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                
                if not info:
                    return {"skipped_date": True}
                    
                upload_date = info.get("upload_date", "99999999")
                if upload_date < "20240101":
                    print(f"⏭️ Video {video_id} is from {upload_date[:4]}. Skipping (Older than 2024).")
                    return {"skipped_date": True}
                    
                metadata = {
                    "video_id": info.get("id", video_id),
                    "title": info.get("title", f"ICT Video {video_id}"),
                    "duration_seconds": info.get("duration", 0),
                    "upload_date": upload_date,
                    "channel": info.get("uploader", "InnerCircleTrader")
                }
        except Exception as e:
            error_msg = str(e)
            print(f"[Error] yt-dlp failed: {error_msg}")
            if "429" in error_msg or "Too Many Requests" in error_msg:
                raise Exception("HTTP_429_BAN")
            return None

        sub_files = glob.glob(os.path.join(self.temp_dir, f"{video_id}*.json3"))
        if not sub_files:
            print(f"[Error] No English subtitle file generated for {video_id}.")
            return {"no_subs": True}
            
        sub_file = sub_files[0]
        
        try:
            with open(sub_file, 'r', encoding='utf-8') as f:
                sub_data = json.load(f)
                
            raw_transcript = []
            for event in sub_data.get('events', []):
                if 'segs' in event:
                    text = "".join([seg.get('utf8', '') for seg in event['segs']]).strip()
                    start = event.get('tStartMs', 0) / 1000.0
                    if text and text != '\n':
                        raw_transcript.append({'text': text, 'start': start})
                        
        except Exception as e:
            print(f"[Error] Failed to parse subtitle JSON: {e}")
            return None
        finally:
            if os.path.exists(sub_file):
                os.remove(sub_file)

        if not raw_transcript:
            print(f"[Error] Transcript was empty for {video_id}.")
            return {"no_subs": True}

        print("[Ingestion] Chunking and Cleaning transcript...")
        raw_chunks = self.chunker.chunk_transcript(raw_transcript)
        
        cleaned_chunks = []
        for chunk in raw_chunks:
            cleaned_text = self.cleaner.clean_text(chunk["text"])
            cleaned_chunks.append({
                "start_time": chunk["start_time"],
                "text": cleaned_text,
                "url_link": f"https://youtu.be/{video_id}?t={int(chunk['start_time'])}s"
            })
            
        metadata["chunks"] = cleaned_chunks
        return metadata