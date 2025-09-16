# -*- coding: utf-8 -*-
from .speech_recognition import SpeechRecognizer
from .text_to_speech import TextToSpeech
from typing import Optional, Callable

class VoiceManager:
    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.text_to_speech = TextToSpeech()

    def speak(self, text: str):
        """Fait parler JARVIS"""
        self.text_to_speech.speak(text)

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Écoute une fois et retourne le texte"""
        return self.speech_recognizer.listen_once(timeout)

    def listen_continuous(self, callback: Callable[[str], None]):
        """Écoute en continu"""
        self.speech_recognizer.listen_continuous(callback)

    def stop_listening(self):
        """Arrête l'écoute continue"""
        self.speech_recognizer.stop_listening()

    def test_voice(self):
        """Test complet du système vocal"""
        print("\n🧪 Test du système vocal...")

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

    def set_voice_settings(self, rate: int = 180, volume: float = 0.9):
        """Configure les paramètres vocaux"""
        self.text_to_speech.set_rate(rate)
        self.text_to_speech.set_volume(volume)