import re
import json

class TaskRouter:
    def __init__(self, l0_commander, l1_model, l2_model, l3_cloud):
        self.l0 = l0_commander
        self.l1 = l1_model
        self.l2 = l2_model
        self.l3 = l3_cloud

    def route(self, query, context=None):
        query_clean = query.lower().strip()
        
        # 1. Heuristic Bypass (STRICT L0 for system actions)
        if query_clean.startswith(("open ", "run ", "start ", "what time")):
            l0_result = self.l0.match_and_execute(query)
            if l0_result:
                return {"level": "L0", "response": l0_result}
            else:
                return {"level": "L0", "response": f"I couldn't find an application named '{query_clean.replace('open ', '')}' on your PC."}

        # 2. Technical Safety Net (Force L2 for technical/math keywords)
        tech_keywords = ["rust", "python", "code", "function", "calculate", "probability", "script", "c#", "protobuf", "math"]
        if any(kw in query_clean for kw in tech_keywords):
            print(f"[Router] Technical keyword detected. Forcing L2...")
            return {"level": "L2", "response": self.l2.process(query, context)}

        # 3. L0 Check (Instant Regex)
        l0_result = self.l0.match_and_execute(query)
        if l0_result:
            return {"level": "L0", "response": l0_result}

        # 3. L1 Intent Classification
        intent = self.l1.classify_intent(query)
        target_level = intent.get("level", "L1")

        if target_level == "L1":
            return {"level": "L1", "response": self.l1.chat(query, context)}
        
        elif target_level == "L2":
            return {"level": "L2", "response": self.l2.process(query, context)}
        
        elif target_level == "L3":
            # Request permission if L3 is suggested
            return {
                "level": "L3_PENDING", 
                "message": "This task requires high-level cloud intelligence. Send to L3?",
                "query": query
            }
        
        return {"level": "L1", "response": self.l1.chat(query, context)}

class IntentModel:
    """Mock for L1 classification until Ollama is hooked up"""
    def classify_intent(self, query):
        query = query.lower()
        if any(word in query for word in ["code", "script", "program", "private", "file"]):
            return {"level": "L2"}
        if any(word in query for word in ["story", "creative", "deep", "invent"]):
            return {"level": "L3"}
        return {"level": "L1"}
