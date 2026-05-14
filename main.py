from core.multi_agent import process_query
from core.memory import MemoryManager
from core.voice_engine import VoiceEngine
import re

def clean_for_speech(text):
    """Remove code blocks, JSON artifacts, and brackets so the voice engine speaks naturally."""
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL) # Remove code blocks
    text = re.sub(r'\{.*?\}', '', text) # Remove inline JSON/brackets
    text = re.sub(r'\[.*?\]', '', text) # Remove square brackets
    return text.strip()

def main():
    memory = MemoryManager()
    voice = VoiceEngine()

    print("--- S.O.F.I.A. Multi-Agent System (LangGraph + RAG) ---")
    print("Système en ligne. 4 Agents prêts. Pipeline RAG activé.")
    
    while True:
        try:
            query = input("\n[Vous]: ")
            if query.lower() in ["exit", "quit", "goodbye", "au revoir"]:
                voice.speak("Au revoir.")
                break

            if not query.strip():
                continue

            # Orchestration via le graphe LangGraph
            print("S.O.F.I.A analyse la requête... ", end="", flush=True)
            
            final_response = process_query(query)
            
            print(f"\nS.O.F.I.A : {final_response}")
            speech_text = clean_for_speech(final_response)
            if speech_text:
                voice.speak(speech_text)
                
            # Update Memory
            is_sensitive = "private" in query.lower()
            memory.add_entry("user", query, is_sensitive)
            memory.add_entry("assistant", final_response, is_sensitive)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[Erreur Système] : {e}")

if __name__ == "__main__":
    main()
