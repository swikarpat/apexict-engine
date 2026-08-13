from apexict.ingestion.youtube_ingest import YouTubeIngestionPipeline

def run_phase1_test():
    print("\n=== APEX-ICT ENGINE: PHASE 1 TEST ===\n")
    
    pipeline = YouTubeIngestionPipeline()
    
    # Using a REAL ICT video: "2022 ICT Mentorship Episode 2"
    test_url = "https://www.youtube.com/watch?v=tmeCWULSTHc"
    
    result = pipeline.process_video(test_url)
    
    if result:
        print("\n✅ --- METADATA EXTRACTED ---")
        print(f"Title: {result['title']}")
        print(f"Channel: {result['channel']}")
        print(f"Total Chunks Generated: {len(result['chunks'])}")
        
        print("\n✅ --- SAMPLE CHUNKS (First 3) ---")
        for i in range(3):
            chunk = result['chunks'][i]
            print(f"\n⏱️ Timestamp: {chunk['start_time']}s")
            print(f"🔗 Link: {chunk['url_link']}")
            print(f"📝 Text: {chunk['text']}")
            
    print("\n=== PHASE 1 SUCCESS ===\n")

if __name__ == "__main__":
    run_phase1_test()