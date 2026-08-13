import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class ICTVectorDB:
    def __init__(self):
        self.client = QdrantClient(path="./ict_qdrant_db")
        # Using your Mac's GPU (mps) for ultra-fast embedding
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2', device='mps')
        self.collection_name = "ict_transcripts"
        self._init_collection()

    def _init_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

    def insert_chunks(self, video_metadata: Dict[str, Any], chunks: List[Dict[str, Any]]):
        points = []
        print(f"[VectorDB] Embedding {len(chunks)} chunks into database...")
        
        for chunk in chunks:
            enriched_text = f"Video Topic: {video_metadata['title']}. Transcript: {chunk['text']}"
            vector = self.encoder.encode(enriched_text).tolist()
            point_id = str(uuid.uuid4())
            
            payload = {
                "video_id": video_metadata["video_id"],
                "title": video_metadata["title"],
                "upload_date": video_metadata.get("upload_date", "20240101"),
                "start_time": chunk["start_time"],
                "text": chunk["text"],
                "url_link": chunk["url_link"]
            }
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))
            
        self.client.upsert(collection_name=self.collection_name, points=points)
        print("[VectorDB] Insertion complete.")

    def search(self, query: str, limit: int = 30) -> List[Dict[str, Any]]:
        query_vector = self.encoder.encode(query).tolist()
        
        # Using the modern Qdrant query_points syntax
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        
        return [point.payload for point in response.points]