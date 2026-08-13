from typing import List, Dict

class TranscriptChunker:
    def __init__(self, chunk_duration_seconds: int = 30):
        self.chunk_duration = chunk_duration_seconds

    def chunk_transcript(self, raw_transcript: List[Dict]) -> List[Dict]:
        """
        Groups raw subtitle lines into ~30-second logical chunks.
        Preserves the exact start time of the chunk.
        """
        chunks = []
        current_text = []
        current_start = 0.0
        
        for item in raw_transcript:
            text = item.get('text', '').replace('\n', ' ')
            start = item.get('start', 0.0)
            
            # Initialize the start time for a new chunk
            if not current_text:
                current_start = start
                
            current_text.append(text)
            
            # If the chunk spans more than our target duration, save it and reset
            if start - current_start >= self.chunk_duration:
                chunks.append({
                    "start_time": round(current_start),
                    "text": " ".join(current_text).strip()
                })
                current_text = []
                
        # Append any remaining text as the final chunk
        if current_text:
            chunks.append({
                "start_time": round(current_start),
                "text": " ".join(current_text).strip()
            })
            
        return chunks