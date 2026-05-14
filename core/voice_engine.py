import pyttsx3
import threading
import queue
import time

class VoiceEngine:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def _speech_worker(self):
        """Dedicated thread to handle the TTS engine loop safely"""
        # Initialize engine inside the worker thread for SAPI5 stability
        engine = pyttsx3.init()
        
        # Configure voice
        voices = engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 180)

        while True:
            try:
                # Wait for text to speak
                text = self.speech_queue.get(timeout=1)
                if text:
                    engine.say(text)
                    engine.runAndWait()
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Voice Error]: {e}")
                time.sleep(1)

    def speak(self, text):
        """Add text to the speech queue"""
        if text:
            print(f"\n[S.O.F.I.A. Speaking...]")
            self.speech_queue.put(text)

    def listen(self):
        """Mock Speech-to-Text"""
        return input("\nVoice Assistant listening (Type here): ")
