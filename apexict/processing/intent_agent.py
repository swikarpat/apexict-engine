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
        
        RULE 1: If the question is a greeting or completely unrelated to trading, output EXACTLY: NON_TRADING_QUERY
        RULE 2: If it IS related to trading, translate it into a highly specific search query using exact ICT terminology.
        RULE 3: DO NOT add any notes, explanations, apologies, or conversational text. Output ONLY the search terms.

        Example 1:
        User: "when market takes equal highs then reversal?"
        Output: Liquidity Sweep of Relative Equal Highs (EQH) leading to Market Structure Shift (MSS)

        Example 2:
        User: "what happens at midnight?"
        Output: NY Midnight Open (00:00 EST) Judas Swing

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