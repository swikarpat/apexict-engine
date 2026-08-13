import requests

class QueryNormalizer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.1:8b"

    def normalize_query(self, raw_query: str) -> str:
        """Translates non-native English into precise ICT search terms, or rejects casual chat."""
        print(f"[Intent Agent] Normalizing raw query: '{raw_query}'")
        
        prompt = f"""
        You are an expert in ICT (Inner Circle Trader) concepts.
        A user is asking a question. 
        
        RULE 1: If the question is a greeting (e.g., "hi", "how are you"), casual conversation, or completely unrelated to trading, finance, or ICT, you MUST output EXACTLY this phrase and nothing else: NON_TRADING_QUERY
        
        RULE 2: If it IS related to trading, translate their question into a clean, highly specific search query using exact ICT terminology (e.g., Fair Value Gap, Liquidity Sweep, Judas Swing, Midnight Open). Only output the optimized search query, nothing else. Do not include quotes.

        User Query: "{raw_query}"
        Output:
        """
        
        try:
            response = requests.post(self.ollama_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }, timeout=15)
            
            optimized_query = response.json()["response"].strip()
            print(f"[Intent Agent] Output: '{optimized_query}'")
            return optimized_query
            
        except Exception as e:
            print(f"[Intent Agent] Error connecting to Ollama: {e}")
            return raw_query