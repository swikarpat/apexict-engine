from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from apexict.db.vector_store import ICTVectorDB
from apexict.processing.intent_agent import QueryNormalizer

app = FastAPI(title="ApexICT Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = ICTVectorDB()
normalizer = QueryNormalizer()

class SearchQuery(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "ApexICT Backend is Active and Ready."}

@app.post("/api/search")
def search_videos(query: SearchQuery):
    print(f"\n[API] Received search query: '{query.text}'")
    
    optimized_query = normalizer.normalize_query(query.text)
    
    if "NON_TRADING_QUERY" in optimized_query:
        print("[API] Non-trading query detected. Rejecting.")
        return {
            "original_query": query.text,
            "optimized_query": "N/A",
            "error": "Please ask only ICT, trading, or market-related questions.",
            "results": []
        }
    
    try:
        # 1. Fetch the Top 30 most relevant chunks
        raw_results = db.search(optimized_query, limit=30)
    except Exception as e:
        print(f"[API] Database search error: {e}")
        raise HTTPException(status_code=500, detail="Database search failed.")
    
    # 2. SORT BY DATE (Newest to Oldest)
    # This guarantees August 2026 comes before July 2026, etc.
    raw_results.sort(key=lambda x: x.get("upload_date", "20240101"), reverse=True)
    
    # 3. Deduplicate and grab the Top 5 Newest & Most Relevant
    unique_results = []
    seen_timestamps = set()
    
    for res in raw_results:
        time_window = int(res["start_time"] // 60) 
        unique_key = f"{res['video_id']}_{time_window}"
        
        if unique_key not in seen_timestamps:
            unique_results.append(res)
            seen_timestamps.add(unique_key)
            
        if len(unique_results) >= 5:
            break
            
    print(f"[API] Returning {len(unique_results)} unique, chronologically sorted video timestamps.")
    
    return {
        "original_query": query.text,
        "optimized_query": optimized_query,
        "error": None,
        "results": unique_results
    }