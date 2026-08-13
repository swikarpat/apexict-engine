import yt_dlp
import time
import random
import os
import sys
from apexict.ingestion.youtube_ingest import YouTubeIngestionPipeline
from apexict.db.vector_store import ICTVectorDB

def get_all_channel_videos(urls: list) -> list:
    """Fetches all URLs instantly, we will filter them using our tracker."""
    ydl_opts = {
        'quiet': True, 
        'extract_flat': True, 
        'force_generic_extractor': False
        # REMOVED the hardcoded 50 limit! It will grab all URLs in ~3 seconds.
    }
    all_video_urls = set()
    
    for url in urls:
        print(f"🔍 Scanning channel for new uploads: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry.get('url'):
                        vid_url = entry['url']
                        if not vid_url.startswith('https://'):
                            vid_url = f"https://www.youtube.com/watch?v={vid_url}"
                        if "/shorts/" not in vid_url:
                            all_video_urls.add(vid_url)
                            
    video_list = list(all_video_urls)
    return video_list

def load_completed_videos() -> set:
    if os.path.exists("completed_videos.txt"):
        with open("completed_videos.txt", "r") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def mark_video_completed(url: str):
    with open("completed_videos.txt", "a") as f:
        f.write(f"{url}\n")

def run_sync():
    print("\n=== APEX-ICT: DELTA SYNC (NEW VIDEOS ONLY) ===\n")
    
    pipeline = YouTubeIngestionPipeline()
    db = ICTVectorDB()
    
    target_urls = [
        "https://www.youtube.com/@InnerCircleTrader/videos",
        "https://www.youtube.com/@InnerCircleTrader/streams"
    ]
    
    # 1. Grab all URLs on the channel (Takes 3 seconds)
    all_urls = get_all_channel_videos(target_urls)
    
    # 2. Load our permanent memory of what we already downloaded
    completed_urls = load_completed_videos()
    
    # 3. The Magic Filter: Only keep URLs that are NOT in our completed list
    new_videos = [url for url in all_urls if url not in completed_urls]
    
    if not new_videos:
        print("✅ Your database is 100% up to date! No new videos found.")
        return

    print(f"🚀 Found {len(new_videos)} NEW videos to ingest!")
    
    success_count = 0
    fail_count = 0
    
    for i, url in enumerate(new_videos):
        print(f"\n[{i+1}/{len(new_videos)}] Processing New Video: {url}")
        
        try:
            metadata = pipeline.process_video(url)
            
            if metadata is None:
                print(f"❌ Processing failed for {url}. Will retry next sync.")
                fail_count += 1
            elif metadata.get("skipped_date"):
                mark_video_completed(url)
            elif metadata.get("no_subs"):
                print(f"⚠️ No transcript found. Marking as skipped.")
                mark_video_completed(url)
                fail_count += 1
            elif metadata.get("chunks"):
                db.insert_chunks(metadata, metadata["chunks"])
                mark_video_completed(url)
                success_count += 1
                
        except Exception as e:
            if "HTTP_429_BAN" in str(e):
                print("\n🚨 [CRITICAL] YouTube IP Ban (429) Detected! Stopping sync.")
                sys.exit(1)
            else:
                print(f"❌ Unknown Error: {e}")
                fail_count += 1
            
        sleep_time = random.uniform(8.0, 14.0)
        print(f"⏳ Sleeping for {round(sleep_time, 1)}s...")
        time.sleep(sleep_time)
        
    print("\n=== 🏁 SYNC COMPLETE 🏁 ===")
    print(f"✅ Successfully Added: {success_count} new videos to your database!")

if __name__ == "__main__":
    run_sync()