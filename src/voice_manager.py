# -*- coding: utf-8 -*-
import speech_recognition as sr
import threading
import queue
import time
from typing import Optional, Callable
from .voice.text_to_speech import TextToSpeech

class VoiceManager:
    def __init__(self):
        # Initialisation de la reconnaissance vocale
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Configuration optimisée pour gérer les pauses et hésitations
        self.recognizer.pause_threshold = 1.2  # Plus de tolérance pour les pauses (défaut: 0.8)
        self.recognizer.non_speaking_duration = 1.0  # Durée avant considérer comme silence
        self.recognizer.phrase_threshold = 0.3  # Sensibilité de détection de début de phrase

        # Initialisation de la synthèse vocale Google TTS
        self.tts = TextToSpeech()

        # Calibrage du micro
        self.calibrate_microphone()

        # Variables pour le contrôle
        self.is_listening = False
        self.voice_queue = queue.Queue()


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
        """Fait parler JARVIS avec Google TTS"""
        try:
            self.tts.speak(text)
        except Exception as e:
            print(f"❌ Erreur synthèse vocale: {e}")

    def listen_once(self, timeout: int = 10) -> Optional[str]:
        """Écoute une fois et retourne le texte reconnu"""
        try:
            print("🎤 Écoute en cours... (prenez votre temps, pauses autorisées)")

            with self.microphone as source:
                # Écouter avec timeout augmenté et phrase_time_limit plus long
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)

            print("🔄 Reconnaissance en cours...")

            # Reconnaissance vocale (français par défaut)
            text = self.recognizer.recognize_google(audio, language='fr-FR')
            print(f"✅ Reconnu: {text}")
            return text

        except sr.WaitTimeoutError:
            print("⏰ Timeout - aucune parole détectée (essayez de parler plus fort)")
            return None
        except sr.UnknownValueError:
            print("❌ Impossible de comprendre l'audio (répétez svp)")
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
                        # Écoute avec paramètres optimisés pour gérer les pauses
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=15)

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