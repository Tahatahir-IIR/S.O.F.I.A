import requests
import json

class OllamaModel:
    def __init__(self, model_name, host="http://localhost:11434"):
        self.host = host
        self.model = model_name

    def generate(self, prompt, system_prompt=None):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True  # Enable streaming
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = requests.post(f"{self.host}/api/generate", json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    token = chunk.get("response", "")
                    full_response += token
                    yield token  # Yield each token for live display
                    if chunk.get("done"):
                        break
        except Exception as e:
            yield f"Error connecting to Ollama: {str(e)}"

class L1Model(OllamaModel):
    """L1: Lightweight conversation (Llama 3.2 1B)"""
    def __init__(self):
        super().__init__("llama3.2:1b")

    def classify_intent(self, query):
        system = (
            "You are a router. Classify the user query into ONE category:\n"
            "L0: If it sounds like a system command (open, run, start, close, what time).\n"
            "L1: Casual conversation, greetings, or general questions.\n"
            "L2: Coding, technical math, or technical reasoning.\n"
            "L3: Creative writing, stories, or deep logic.\n"
            "Response format: Return ONLY the code (e.g., L0)."
        )
        response = "".join(list(self.generate(query, system_prompt=system))).strip().upper()
        
        for level in ["L0", "L1", "L2", "L3"]:
            if level in response:
                return {"level": level}
        return {"level": "L1"}

    def chat(self, query, context=""):
        prompt = f"Context: {context}\nUser: {query}"
        system = "You are S.O.F.I.A, a helpful local AI. You MUST speak ONLY in English. Do not use other languages."
        return self.generate(prompt, system_prompt=system)

class L2Model(OllamaModel):
    """L2: Advanced Local (Qwen 3.5 4B or Phi-4 Mini)"""
    def __init__(self):
        # We will try Qwen first, then Phi-4 Mini
        super().__init__("qwen3.5:4b")
        self.fallback_model = "phi4-mini:latest"

    def process(self, query, context=""):
        print(f"[L2] Attempting generation with {self.model}...")
        try:
            # Try primary model
            return self.generate(query, system_prompt="You are a senior technical assistant. Speak ONLY in English.")
        except Exception:
            print(f"[L2] {self.model} failed. Falling back to {self.fallback_model}...")
            self.model = self.fallback_model
            return self.generate(query, system_prompt="You are a senior technical assistant. Speak ONLY in English.")

class L3Cloud:
    """L3: Cloud Intelligence (Placeholder for API)"""
    def query(self, query, context=""):
        # Just a simple generator for consistency
        yield f"[L3 - Cloud Placeholder] High-level reasoning results for: {query}"
