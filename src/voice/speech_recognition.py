# -*- coding: utf-8 -*-
import speech_recognition as sr
import threading
import queue
import time
from typing import Optional, Callable

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.voice_queue = queue.Queue()

        # Calibrage automatique
        self.calibrate_microphone()

    def calibrate_microphone(self):
        """Calibre le microphone pour réduire le bruit ambiant"""
        try:
            print("🎤 Calibrage du microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibré !")
        except Exception as e:
            print(f"⚠️ Erreur calibrage micro: {e}")

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Écoute une fois et retourne le texte reconnu"""
        try:
            print("🎤 Écoute en cours... (parlez maintenant)")

            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            print("🔄 Reconnaissance en cours...")

            # Reconnaissance vocale français
            text = self.recognizer.recognize_google(audio, language='fr-FR')
            print(f"✅ Reconnu: {text}")
            return text

        except sr.WaitTimeoutError:
            print("⏰ Timeout - aucune parole détectée")
            return None
        except sr.UnknownValueError:
            print("❌ Impossible de comprendre l'audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Erreur service reconnaissance: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur écoute: {e}")
            return None

    def listen_continuous(self, callback: Callable[[str], None]):
        """Écoute en continu et appelle le callback pour chaque phrase"""
        def listen_worker():
            print("🎤 Écoute continue activée")

            while self.is_listening:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)

                    try:
                        text = self.recognizer.recognize_google(audio, language='fr-FR')

                        # Vérifier commande d'arrêt
                        if any(word in text.lower() for word in ['arrêter', 'stop', 'pause', 'silence']):
                            print("🔇 Écoute continue désactivée")
                            self.is_listening = False
                            break

                        callback(text)

                    except (sr.UnknownValueError, sr.RequestError):
                        pass

                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Erreur écoute continue: {e}")
                    time.sleep(1)

        self.is_listening = True
        listen_thread = threading.Thread(target=listen_worker, daemon=True)
        listen_thread.start()

    def stop_listening(self):
        """Arrête l'écoute continue"""
        self.is_listening = False