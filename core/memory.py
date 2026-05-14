import json
import os

class MemoryManager:
    def __init__(self, storage_path="C:/S.O.F.I.A/outputs/memory.json"):
        self.storage_path = storage_path
        self.short_term = []
        self.max_history = 10
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def add_entry(self, role, content, is_sensitive=False):
        entry = {
            "role": role,
            "content": content,
            "sensitive": is_sensitive
        }
        
        # Never store sensitive data in persistent storage
        if not is_sensitive:
            self.short_term.append(entry)
            if len(self.short_term) > self.max_history:
                self.short_term.pop(0)
            self._persist()

    def get_context(self):
        return "\n".join([f"{e['role']}: {e['content']}" for e in self.short_term])

    def _persist(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.short_term, f, indent=4)
        except Exception as e:
            print(f"Memory persistence error: {e}")
