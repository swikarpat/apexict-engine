from apexict.ingestion.youtube_ingest import YouTubeIngestionPipeline
from apexict.db.vector_store import ICTVectorDB
from apexict.processing.intent_agent import QueryNormalizer

def run_phase2_test():
    print("\n=== APEX-ICT ENGINE: PHASE 2 TEST ===\n")
    
    # 1. Initialize our modules
    pipeline = YouTubeIngestionPipeline()
    db = ICTVectorDB()
    normalizer = QueryNormalizer()
    
    # 2. Ingest the video and save to Database
    test_url = "https://www.youtube.com/watch?v=tmeCWULSTHc" # ICT Ep 2
    metadata = pipeline.process_video(test_url)
    
    if metadata:
        db.insert_chunks(metadata, metadata["chunks"])
        
    # 3. The User asks a question in non-native English
    print("\n--- SEARCHING THE DATABASE ---")
    raw_user_query = "when market takes relative equal highs then when it reversal?"
    
    # 4. Normalize the query using Ollama
    optimized_query = normalizer.normalize_query(raw_user_query)
    
    # 5. Search the Vector Database
    results = db.search(optimized_query, limit=2)
    
    print("\n🎯 --- TOP VIDEO MATCHES ---")
    for i, res in enumerate(results):
        print(f"\nMatch {i+1}: {res['title']}")
        print(f"🔗 Click to watch: {res['url_link']}")
        print(f"📝 Transcript Context: {res['text']}")

    print("\n=== PHASE 2 SUCCESS ===\n")

if __name__ == "__main__":
    run_phase2_test()