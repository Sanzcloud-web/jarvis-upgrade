# -*- coding: utf-8 -*-
import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from typing import Optional, Callable

class VoiceManager:
    def __init__(self):
        # Initialisation de la reconnaissance vocale
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialisation de la synthèse vocale
        self.tts_engine = pyttsx3.init()
        self.setup_tts()

        # Calibrage du micro
        self.calibrate_microphone()

        # Variables pour le contrôle
        self.is_listening = False
        self.voice_queue = queue.Queue()

    def setup_tts(self):
        """Configure la synthèse vocale"""
        try:
            # Réglages de la voix
            voices = self.tts_engine.getProperty('voices')

            # Chercher une voix française si disponible
            french_voice = None
            for voice in voices:
                if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                    french_voice = voice
                    break

            if french_voice:
                self.tts_engine.setProperty('voice', french_voice.id)

            # Réglages de vitesse et volume
            self.tts_engine.setProperty('rate', 180)  # Vitesse de parole
            self.tts_engine.setProperty('volume', 0.9)  # Volume

        except Exception as e:
            print(f"⚠️ Erreur configuration TTS: {e}")

    def calibrate_microphone(self):
        """Calibre le microphone pour réduire le bruit ambiant"""
        try:
            print("🎤 Calibrage du microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibré !")
        except Exception as e:
            print(f"⚠️ Erreur calibrage micro: {e}")

    def speak(self, text: str):
        """Fait parler JARVIS"""
        try:
            print(f"🔊 JARVIS dit: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ Erreur synthèse vocale: {e}")

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Écoute une fois et retourne le texte reconnu"""
        try:
            print("🎤 Écoute en cours... (parlez maintenant)")

            with self.microphone as source:
                # Écouter avec timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            print("🔄 Reconnaissance en cours...")

            # Reconnaissance vocale (français par défaut)
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
            print("🎤 Écoute continue activée - dites 'arrêter' pour désactiver")

            while self.is_listening:
                try:
                    with self.microphone as source:
                        # Écoute avec timeout court pour permettre l'arrêt
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)

                    # Reconnaissance en arrière-plan
                    try:
                        text = self.recognizer.recognize_google(audio, language='fr-FR')

                        # Vérifier commande d'arrêt
                        if any(word in text.lower() for word in ['arrêter', 'stop', 'pause', 'silence']):
                            print("🔇 Écoute continue désactivée")
                            self.is_listening = False
                            break

                        # Appeler le callback avec le texte reconnu
                        callback(text)

                    except (sr.UnknownValueError, sr.RequestError):
                        # Ignorer les erreurs de reconnaissance en mode continu
                        pass

                except sr.WaitTimeoutError:
                    # Continue à écouter
                    continue
                except Exception as e:
                    print(f"❌ Erreur écoute continue: {e}")
                    time.sleep(1)

        # Démarrer l'écoute en arrière-plan
        self.is_listening = True
        listen_thread = threading.Thread(target=listen_worker, daemon=True)
        listen_thread.start()

    def stop_listening(self):
        """Arrête l'écoute continue"""
        self.is_listening = False

    def test_voice(self):
        """Test des fonctionnalités vocales"""
        print("\n🧪 Test des fonctionnalités vocales...")

        # Test TTS
        self.speak("Bonjour ! Je suis JARVIS, votre assistant vocal.")

        # Test reconnaissance
        print("\n📝 Test de reconnaissance vocale:")
        result = self.listen_once(timeout=10)

        if result:
            self.speak(f"J'ai compris: {result}")
            return True
        else:
            self.speak("Je n'ai pas réussi à vous comprendre.")
            return False