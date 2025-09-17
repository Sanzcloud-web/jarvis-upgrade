# -*- coding: utf-8 -*-
import speech_recognition as sr  # pyright: ignore[reportMissingImports]
import threading
import queue
import time
from typing import Optional, Callable
from .voice.text_to_speech import TextToSpeech
from .voice.speech_recognition import SpeechRecognizer
from .utils.system_utils import system_detector

class VoiceManager:
    def __init__(self):
        # Utiliser la nouvelle classe SpeechRecognizer avec activation par mot-clé
        self.speech_recognizer = SpeechRecognizer()
        
        # Garder une référence directe pour compatibilité
        self.recognizer = self.speech_recognizer.recognizer
        self.microphone = self.speech_recognizer.microphone

        # Initialisation de la synthèse vocale optimisée
        self.tts = TextToSpeech()

        # Variables pour le contrôle
        self.is_listening = False
        self.voice_queue = queue.Queue()
        self.interrupt_monitor_active = False
        
        print(f"🎯 VoiceManager initialisé avec activation par mot-clé '{self.speech_recognizer.wake_word}'")


    def speak(self, text: str):
        """Fait parler JARVIS sans surveillance d'interruption automatique"""
        try:
            print("💡 Appuyez sur [CTRL+C] pour interrompre JARVIS si nécessaire")
            
            # Faire parler JARVIS avec vitesse optimisée
            self.tts.speak(text)

        except KeyboardInterrupt:
            print("🔇 JARVIS interrompu par l'utilisateur")
            self.tts.stop_speaking()
        except Exception as e:
            print(f"❌ Erreur synthèse vocale: {e}")

    def listen_once(self, timeout: int = 10) -> Optional[str]:
        """Écoute une fois avec activation par mot-clé JARVIS"""
        return self.speech_recognizer.listen_once(timeout)
    
    def set_wake_word_mode(self, enabled: bool):
        """Active ou désactive l'exigence du mot-clé 'jarvis'"""
        self.speech_recognizer.set_wake_word_required(enabled)
        
    def disable_wake_word_temporarily(self):
        """Désactive temporairement le mot-clé (pour tests ou configuration)"""
        self.speech_recognizer.set_wake_word_required(False)
    
    def enable_response_mode(self):
        """Active le mode attente de réponse conversationnelle"""
        self.speech_recognizer.enable_response_mode()
        
    def disable_response_mode(self):
        """Désactive le mode attente de réponse"""
        self.speech_recognizer.disable_response_mode()
        
    def is_waiting_for_response(self) -> bool:
        """Vérifie si on attend une réponse"""
        return self.speech_recognizer.is_waiting_for_response()

    def listen_continuous(self, callback: Callable[[str], None]):
        """Écoute en continu avec activation par mot-clé JARVIS"""
        # Utiliser le système d'écoute continue avec mot-clé
        self.speech_recognizer.listen_continuous(callback)
        self.is_listening = self.speech_recognizer.is_listening

    def stop_listening(self):
        """Arrête l'écoute continue"""
        self.speech_recognizer.stop_listening()
        self.is_listening = False

    def start_interrupt_monitor(self):
        """Démarre la surveillance d'interruption avec détection audio améliorée"""
        if self.interrupt_monitor_active:
            return

        self.interrupt_monitor_active = True
        print("🎤 Surveillance d'interruption activée - parlez FORT pour interrompre JARVIS")

        def audio_interrupt_worker():
            # Configuration plus stricte pour éviter les faux positifs
            temp_recognizer = sr.Recognizer()
            temp_recognizer.energy_threshold = self.recognizer.energy_threshold * 2  # Seuil plus élevé
            temp_recognizer.pause_threshold = 0.5  # Plus de tolérance
            
            while self.interrupt_monitor_active and self.tts.is_speaking:
                try:
                    with self.microphone as source:
                        # Écoute plus longue avec seuil plus élevé pour éviter les faux positifs
                        audio = temp_recognizer.listen(source, timeout=0.5, phrase_time_limit=1.0)
                        
                    # Essayer de reconnaître pour s'assurer que c'est vraiment de la parole
                    try:
                        text = temp_recognizer.recognize_google(audio, language='fr-FR')
                        # Si on arrive ici, c'est vraiment de la parole
                        if len(text.strip()) > 2:  # Au moins 3 caractères pour éviter les bruits
                            print(f"🎤 Interruption détectée : '{text}'")
                            self.tts.stop_speaking()
                            self.interrupt_monitor_active = False
                            break
                    except (sr.UnknownValueError, sr.RequestError):
                        # Si on ne peut pas reconnaître, c'est probablement du bruit
                        continue
                        
                except sr.WaitTimeoutError:
                    # Pas de son détecté, continuer
                    continue
                except Exception:
                    # Ignorer les autres erreurs
                    time.sleep(0.2)
                    continue

        # Démarrer la surveillance en arrière-plan
        monitor_thread = threading.Thread(target=audio_interrupt_worker, daemon=True)
        monitor_thread.start()
    

    def stop_interrupt_monitor(self):
        """Arrête la surveillance d'interruption"""
        self.interrupt_monitor_active = False

    def test_voice(self):
        """Test des fonctionnalités vocales avec activation par mot-clé"""
        print("\n🧪 Test des fonctionnalités vocales avec JARVIS...")

        # Test TTS avec vitesse optimisée
        self.speak("Bonjour ! Je suis JARVIS, votre assistant vocal avec activation par mot-clé.")

        # Test reconnaissance avec mot-clé
        print(f"\n📝 Test de reconnaissance vocale avec mot-clé '{self.speech_recognizer.wake_word}':")
        print(f"💡 Dites: '{self.speech_recognizer.wake_word}' suivi de votre message")
        
        result = self.listen_once(timeout=15)

        if result:
            self.speak(f"Parfait ! J'ai compris votre demande: {result}")
            return True
        else:
            self.speak(f"N'oubliez pas de dire '{self.speech_recognizer.wake_word}' avant votre message.")
            return False