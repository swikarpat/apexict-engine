import yt_dlp
import time
import random
import os
import sys
from apexict.ingestion.youtube_ingest import YouTubeIngestionPipeline
from apexict.db.vector_store import ICTVectorDB

def get_all_channel_videos(urls: list) -> list:
    ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_extractor': False}
    all_video_urls = set()
    
    for url in urls:
        print(f"🔍 Scanning tab: {url}")
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
    print(f"✅ Found {len(video_list)} unique long-form videos & streams!")
    return video_list

def load_completed_videos() -> set:
    if os.path.exists("completed_videos.txt"):
        with open("completed_videos.txt", "r") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def mark_video_completed(url: str):
    with open("completed_videos.txt", "a") as f:
        f.write(f"{url}\n")

def run_bulk_ingestion():
    print("\n=== APEX-ICT: 2023-PRESENT INGESTION ===\n")
    
    pipeline = YouTubeIngestionPipeline()
    db = ICTVectorDB()
    
    target_urls = [
        "https://www.youtube.com/@InnerCircleTrader/videos",
        "https://www.youtube.com/@InnerCircleTrader/streams"
    ]
    
    video_urls = get_all_channel_videos(target_urls)
    completed_urls = load_completed_videos()
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    print(f"\n🚀 Found {len(completed_urls)} already completed videos. Skipping those...")
    
    for i, url in enumerate(video_urls):
        print(f"\n[{i+1}/{len(video_urls)}] Processing: {url}")
        
        if url in completed_urls:
            print("⏭️ Already processed. Skipping without hitting YouTube.")
            skipped_count += 1
            continue
            
        try:
            metadata = pipeline.process_video(url)
            
            # CRITICAL FIX: If metadata is None, it means a hard crash happened. Do NOT mark as completed!
            if metadata is None:
                print(f"❌ Processing failed for {url}. Will retry next time.")
                fail_count += 1
                
            elif metadata.get("skipped_date"):
                mark_video_completed(url)
                skipped_count += 1
                continue # Skip sleep timer
                
            elif metadata.get("no_subs"):
                print(f"⚠️ No transcript found for {url}. Marking as skipped.")
                mark_video_completed(url)
                fail_count += 1
                
            elif metadata.get("chunks"):
                db.insert_chunks(metadata, metadata["chunks"])
                mark_video_completed(url)
                success_count += 1
                
        except Exception as e:
            if "HTTP_429_BAN" in str(e):
                print("\n🚨 [CRITICAL] YouTube IP Ban (429) Detected!")
                print("🚨 Stopping the script immediately to protect your progress.")
                sys.exit(1)
            else:
                print(f"❌ Unknown Error processing {url}: {e}")
                fail_count += 1
            
        sleep_time = random.uniform(8.0, 14.0)
        print(f"⏳ Sleeping for {round(sleep_time, 1)}s to mimic human behavior...")
        time.sleep(sleep_time)
        
    print("\n=== 🏁 FULL INGESTION COMPLETE 🏁 ===")
    print(f"✅ Successfully Indexed: {success_count} videos")
    print(f"⏭️ Skipped (Old/Already Done): {skipped_count} videos")
    print(f"❌ Failed/No Transcript: {fail_count} videos")

if __name__ == "__main__":
    run_bulk_ingestion()